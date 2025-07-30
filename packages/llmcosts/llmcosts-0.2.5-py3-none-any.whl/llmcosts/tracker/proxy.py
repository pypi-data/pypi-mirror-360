"""
Main LLM tracking proxy that wraps any LLM client and tracks usage.
"""

import functools
import inspect
import json
import logging
import os
from typing import Any, Callable, Dict, Optional

from ..client import LLMCostsClient
from ..exceptions import TriggeredLimitError
from .frameworks import Framework
from .providers import Provider
from .registry import get_usage_handler
from .usage_delivery import UsageTracker, get_usage_tracker, set_global_usage_tracker


class LLMTrackingProxy:
    """
    Wrap ANY client or sub-client (OpenAI(), Anthropic(), genai.GenerativeModel, etc.).
    Internally uses :class:`LLMCostsClient` for all HTTP communication so that
    connectivity settings remain consistent across the SDK.

    The ``provider`` parameter specifies the actual LLM service (e.g., OpenAI, Anthropic)
    and is required for all usage. The ``framework`` parameter is optional and only needed
    for special integrations like LangChain. Most users should omit ``framework`` (defaults to None).

    Examples:
        import openai
        import anthropic
        from tracker import LLMTrackingProxy, Provider, Framework

        # Standard usage - framework=None by default
        openai_client = LLMTrackingProxy(
            openai.OpenAI(),
            provider=Provider.OPENAI  # Required: specifies the LLM service
        )

        anthropic_client = LLMTrackingProxy(
            anthropic.Anthropic(),
            provider=Provider.ANTHROPIC  # Required: specifies the LLM service
        )

        # OpenAI-compatible APIs (DeepSeek, Grok, etc.) - base_url auto-extracted
        deepseek_client = openai.OpenAI(
            api_key="your-key",
            base_url="https://api.deepseek.com/v1"
        )
        tracked_deepseek = LLMTrackingProxy(
            deepseek_client,
            provider=Provider.OPENAI  # base_url automatically extracted from client
        )

        # LangChain integration - framework parameter required
        from langchain_openai import ChatOpenAI
        tracked_client = LLMTrackingProxy(
            openai.OpenAI(),
            provider=Provider.OPENAI,        # Required: the underlying LLM provider
            framework=Framework.LANGCHAIN    # Required: enables LangChain features
        )
        chat_model = ChatOpenAI(client=tracked_client.chat.completions)

        # Usage tracking works automatically for all cases
        openai_response = openai_client.chat.completions.create(...)
        anthropic_response = anthropic_client.messages.create(...)
    """

    def __init__(
        self,
        target: Any,
        provider: Provider,
        framework: Optional[Framework] = None,
        debug: bool = False,
        sync_mode: bool = False,
        remote_save: bool = True,
        context: Optional[Dict[str, Any]] = None,
        response_callback: Optional[Callable[[Any], None]] = None,
        api_key: Optional[str] = None,
        client_customer_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the tracking proxy.

        Args:
            target: The LLM client to wrap (OpenAI, Anthropic, etc.)
            provider: The Provider enum value specifying which LLM service this is.
                     Required for all usage (e.g., Provider.OPENAI, Provider.ANTHROPIC).
            framework: Optional framework integration (e.g., ``Framework.LANGCHAIN``).
                      Usually ``None`` (default) for direct API usage. Only needed for
                      special integrations like LangChain that require framework-specific
                      features (e.g., automatic stream options injection).
            debug: If True, enable debug logging. Otherwise logs errors only.
            sync_mode: If True, wait for the usage tracker to return (good for debugging/testing).
            remote_save: If True, tell the remote server to save cost events.
            context: Optional context dictionary to include in usage payloads.
            response_callback: Optional callback function to call with LLM responses.
            api_key: Optional LLMCOSTS_API_KEY. If None, will check environment variables.
                    If not found in environment either, will raise an error.
            client_customer_key: Optional customer key for multi-tenant applications.
            base_url: Optional base URL for OpenAI-compatible endpoints. If not provided,
                will automatically extract from the target client's base_url attribute
                (e.g., from OpenAI client). This value will be included in usage payloads
                for completions tracking.
        """
        self._target = target
        self._provider = provider
        self._debug = debug  # Store debug setting to preserve it for child proxies
        self._framework = framework
        self._sync_mode = sync_mode
        self._remote_save = remote_save
        self._context = context.copy() if context else None
        self._response_callback = response_callback
        self._client_customer_key = client_customer_key

        # Auto-extract base_url from OpenAI client if not provided
        if base_url is None and hasattr(target, "base_url"):
            # Convert URL object to string if needed
            extracted_url = target.base_url
            if hasattr(extracted_url, "__str__"):
                self._base_url = str(extracted_url)
            else:
                self._base_url = extracted_url
        else:
            self._base_url = base_url

        self._usage_handler = get_usage_handler(target)
        self._langchain_mode = False  # Initialize LangChain compatibility mode

        # Handle API key and set up tracker
        self._setup_tracker(api_key, sync_mode)

        # Enable framework-specific behavior
        if self._framework == Framework.LANGCHAIN:
            self.enable_langchain_mode()

        # When debugging, set the root logger level to DEBUG.
        # This is necessary for pytest's caplog to capture the messages.
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        else:
            logging.getLogger().setLevel(logging.ERROR)

    def _setup_tracker(self, api_key: Optional[str], sync_mode: bool) -> None:
        """Set up the usage tracker with API key validation.

        Creates a :class:`LLMCostsClient` configured with the resolved API key
        and passes it to :class:`UsageTracker` so that all network operations use
        the same HTTP session.
        """
        # If this is a child proxy (api_key=None), try to get client from existing tracker
        if api_key is None:
            try:
                existing_tracker = get_usage_tracker()
                if (
                    existing_tracker
                    and existing_tracker.api_key
                    and hasattr(existing_tracker, "client")
                ):
                    # Use the client from the existing tracker
                    self._llm_costs_client = existing_tracker.client
                    return
            except:
                pass  # Fall through to error handling

            # If we reach here, no existing tracker was found but api_key is None
            # This means we're a child proxy but there's no parent tracker set up
            raise ValueError(
                "Child proxy created without a parent tracker. Ensure the parent "
                "LLMTrackingProxy is initialized with a valid LLMCOSTS_API_KEY."
            )

        # Determine the API key to use
        final_api_key = api_key or os.environ.get("LLMCOSTS_API_KEY")

        if not final_api_key:
            raise ValueError(
                "LLMCOSTS_API_KEY is required. Please provide it as a parameter to "
                "LLMTrackingProxy() or set the LLMCOSTS_API_KEY environment variable."
            )

        # Create a custom tracker with the API key
        api_endpoint = os.environ.get(
            "LLMCOSTS_API_ENDPOINT", "https://llmcosts.com/api/v1/usage"
        )
        client = LLMCostsClient(
            api_key=final_api_key,
            base_url=api_endpoint.rsplit("/", 1)[0],
            framework=self._framework.value if self._framework else None,
        )
        tracker = UsageTracker(
            api_endpoint=api_endpoint,
            api_key=final_api_key,
            sync_mode=sync_mode,
            client=client,
        )

        # Store the client for threshold checking
        self._llm_costs_client = client

        # Start the tracker if not in sync mode
        if not sync_mode:
            tracker.start()

        # Set this as the global tracker
        set_global_usage_tracker(tracker)

    def _is_llm_call(self, attr: Callable) -> bool:
        """Heuristically determine if the call sends tokens to an LLM."""
        name = getattr(attr, "__name__", "").lower()
        owner = str(getattr(attr, "__self__", "")).lower()

        if "completions" in owner and name == "create":
            return True
        if "messages" in owner and name in {"create", "stream"}:
            return True
        if "invoke_model" in name or "converse" in name or "converse" in owner:
            return True
        if "generate_content" in name:
            return True
        if "responses" in owner and name == "create":
            return True
        return False

    def _select_violation(self, violations: list[dict]) -> dict:
        """Return the most limiting violation from a list."""
        if not violations:
            return {}

        def _amount(v):
            try:
                return float(v.get("amount", float("inf")))
            except Exception:
                return float("inf")

        return min(violations, key=_amount)

    def _check_triggered_thresholds(
        self, attr: Callable, args: tuple, kw: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check triggered thresholds before making LLM call."""
        if not hasattr(self, "_llm_costs_client"):
            # No client available for threshold checking, allow the call
            return {"status": "no_client", "allowed": True, "violations": []}

        # Extract model information from kwargs or args
        model_id = kw.get("model") or kw.get("modelId") or kw.get("model_id")
        if model_id is None:
            try:
                sig = inspect.signature(attr)
                params = list(sig.parameters.keys())
                for idx, p in enumerate(params):
                    if p in {"model", "modelId", "model_id"} and idx < len(args):
                        model_id = args[idx]
                        break
            except Exception:
                pass

        result = self._llm_costs_client.check_triggered_thresholds(
            provider=self._provider.value,
            model_id=model_id,
            client_key=self._client_customer_key,
        )

        # If the mocked client returns a non-dict (e.g., MagicMock),
        # fallback to an empty result to avoid errors during testing.
        if not isinstance(result, dict):
            return {"status": "no_client", "allowed": True, "violations": []}

        # Log warnings for alerts
        if result.get("warnings"):
            logging.warning("⚠️ Triggered threshold ALERT detected:")
            for warning in result["warnings"]:
                logging.warning(f"   • {warning['message']}")
                logging.warning(
                    f"   • Threshold: {warning.get('threshold_type', 'unknown')} - ${warning.get('amount', 'unknown')}"
                )

        # Log violations for limits
        if result.get("violations"):
            logging.error("🚫 Triggered threshold LIMIT detected:")
            for violation in result["violations"]:
                logging.error(f"   • {violation['message']}")
                logging.error(
                    f"   • Threshold: {violation.get('threshold_type', 'unknown')} - ${violation.get('amount', 'unknown')}"
                )

        # Log when no triggered thresholds are found
        if result["status"] == "no_triggered_thresholds":
            logging.debug("✅ No triggered thresholds found - call proceeding normally")
        elif (
            result["status"] == "checked"
            and not result.get("violations")
            and not result.get("warnings")
        ):
            logging.debug("✅ Triggered thresholds checked - no violations or warnings")

        return result

    @property
    def provider_name(self) -> str:
        """Get the name of the detected provider."""
        return self._usage_handler.provider_name

    @property
    def provider(self) -> Provider:
        """Get the provider enum value."""
        return self._provider

    @property
    def framework(self) -> Optional[Framework]:
        """Get the framework this proxy was initialized with."""
        return self._framework

    @property
    def sync_mode(self) -> bool:
        """Get the current sync_mode setting."""
        return self._sync_mode

    @sync_mode.setter
    def sync_mode(self, value: bool) -> None:
        """Set the sync_mode setting."""
        self._sync_mode = value

    @property
    def remote_save(self) -> bool:
        """Get the current remote_save setting."""
        return self._remote_save

    @remote_save.setter
    def remote_save(self, value: bool) -> None:
        """Set the remote_save setting."""
        self._remote_save = value

    @property
    def context(self) -> Optional[Dict[str, Any]]:
        """Get the current context setting."""
        return self._context.copy() if self._context else None

    @context.setter
    def context(self, value: Optional[Dict[str, Any]]) -> None:
        """Set the context setting."""
        self._context = value.copy() if value else None

    @property
    def response_callback(self) -> Optional[Callable[[Any], None]]:
        """Get the current response_callback setting."""
        return self._response_callback

    @response_callback.setter
    def response_callback(self, value: Optional[Callable[[Any], None]]) -> None:
        """Set the response_callback setting."""
        self._response_callback = value

    @property
    def client_customer_key(self) -> Optional[str]:
        """Get the current client_customer_key setting."""
        return self._client_customer_key

    @client_customer_key.setter
    def client_customer_key(self, value: Optional[str]) -> None:
        """Set the client_customer_key setting."""
        self._client_customer_key = value

    @property
    def base_url(self) -> Optional[str]:
        """Get the base_url used for OpenAI-compatible calls."""
        return self._base_url

    @base_url.setter
    def base_url(self, value: Optional[str]) -> None:
        """Set the base_url for subsequent calls."""
        self._base_url = value

    def enable_langchain_mode(self) -> None:
        """Enable LangChain compatibility mode.

        This allows sub-clients to automatically inject stream_options for seamless
        LangChain integration while maintaining strict validation for direct usage.
        """
        self._langchain_mode = True

    # --------------------------------------------------------------------- #
    # Usage output - log via Python logging module
    # --------------------------------------------------------------------- #
    def _track_usage(self, payload: Optional[Dict]):
        """Enqueue payload for delivery and log if available."""
        if payload is None:
            return

        # Add provider to payload
        payload["provider"] = self._provider.value

        # Add remote_save flag to payload if not True (default)
        if not self._remote_save:
            payload["remote_save"] = False

        # Add context to payload if available
        if self._context:
            payload["context"] = self._context

        # Add client_customer_key to payload if set (including None)
        if hasattr(self, "_client_customer_key"):
            payload["client_customer_key"] = self._client_customer_key

        # Use global tracker for safety - ensures delivery even if proxy goes out of scope
        get_usage_tracker().track(payload)
        logging.debug(
            "[LLM costs] %s usage → %s",
            self.provider_name,
            json.dumps(payload),
        )

    def _call_response_callback(self, response: Any) -> None:
        """Call the response callback if available."""
        if self._response_callback:
            try:
                self._response_callback(response)
            except Exception as e:
                logging.error(f"Error in response callback: {e}")

    # --------------------------------------------------------------------- #
    # Reflection magic: forward every attribute or call
    # --------------------------------------------------------------------- #
    def __getattr__(self, item: str):
        attr = getattr(self._target, item)

        # Namespace attributes (.chat, .messages, .models, etc.)
        if not callable(attr):
            child_proxy = self.__class__(
                attr,
                provider=self._provider,
                framework=self._framework,
                debug=self._debug,
                sync_mode=self._sync_mode,
                remote_save=self._remote_save,
                context=self._context,
                response_callback=self._response_callback,
                api_key=None,  # Child proxies use the already-set global tracker
                client_customer_key=self._client_customer_key,
                base_url=self._base_url,
            )
            # Pass the client reference to the child proxy for threshold checking
            child_proxy._llm_costs_client = self._llm_costs_client

            # Sub-clients inherit the auto-injection setting from parent
            if hasattr(self, "_langchain_mode") and self._langchain_mode:
                child_proxy._target._auto_inject_stream_options = True
                child_proxy._langchain_mode = True

            return child_proxy

        # ------------------ async callables ------------------ #
        if inspect.iscoroutinefunction(attr):

            async def a_wrapper(*args, **kw):
                threshold_check = self._check_triggered_thresholds(attr, args, kw)
                if self._is_llm_call(attr) and threshold_check.get("violations"):
                    violation = self._select_violation(threshold_check["violations"])
                    raise TriggeredLimitError(violation)

                # Validate streaming options before making the call
                self._usage_handler.validate_streaming_options(self._target, kw, attr)

                res = await attr(*args, **kw)

                # Call response callback with the response
                self._call_response_callback(res)

                # streaming?
                if kw.get("stream") or "stream" in attr.__name__:

                    async def agen():
                        last_chunk = None
                        usage_found = False

                        # Get the correct iterator for streaming (handles Bedrock's special structure)
                        iterator = res
                        if hasattr(self._usage_handler, "get_streaming_iterator"):
                            iterator = self._usage_handler.get_streaming_iterator(
                                res, attr
                            )

                        async for chunk in iterator:
                            payload = self._usage_handler.extract_usage_payload(
                                chunk, **kw, attr=attr, base_url=self._base_url
                            )
                            if payload:
                                usage_found = True
                            self._track_usage(payload)
                            last_chunk = chunk

                            # Call response callback with each chunk
                            self._call_response_callback(chunk)

                            yield chunk

                        if last_chunk and not usage_found:
                            payload = self._usage_handler.extract_usage_payload(
                                last_chunk, **kw, attr=attr, base_url=self._base_url
                            )
                            self._track_usage(payload)

                    return agen()

                payload = self._usage_handler.extract_usage_payload(
                    res, **kw, attr=attr, base_url=self._base_url
                )
                self._track_usage(payload)
                return res

            return functools.wraps(attr)(a_wrapper)

        # ------------------ sync callables ------------------- #
        def s_wrapper(*args, **kw):
            threshold_check = self._check_triggered_thresholds(attr, args, kw)
            if self._is_llm_call(attr) and threshold_check.get("violations"):
                violation = self._select_violation(threshold_check["violations"])
                raise TriggeredLimitError(violation)

            # Validate streaming options before making the call
            self._usage_handler.validate_streaming_options(self._target, kw, attr)

            res = attr(*args, **kw)

            # Call response callback with the response
            self._call_response_callback(res)

            if kw.get("stream") or "stream" in attr.__name__:
                # Check if the response is a context manager (like OpenAI chat completions)
                # If it has __enter__ and __exit__, it's a context manager
                if hasattr(res, "__enter__") and hasattr(res, "__exit__"):
                    # Create a wrapper that can work both as an iterator and context manager
                    class StreamingWrapper:
                        def __init__(
                            self,
                            response,
                            tracker_func,
                            usage_handler,
                            callback_func,
                            kw,
                            attr,
                            base_url,
                        ):
                            self._response = response
                            self._tracker_func = tracker_func
                            self._usage_handler = usage_handler
                            self._callback_func = callback_func
                            self._kw = kw
                            self._attr = attr
                            self._base_url = base_url
                            self._stream = None
                            self._iterator = None

                        def __enter__(self):
                            # For ChatOpenAI context manager usage
                            self._stream = self._response.__enter__()
                            return self

                        def __exit__(self, exc_type, exc_val, exc_tb):
                            # For ChatOpenAI context manager usage
                            return self._response.__exit__(exc_type, exc_val, exc_tb)

                        def __iter__(self):
                            # For both direct iteration and context manager iteration
                            if self._stream is not None:
                                # We're in a context manager, iterate over the stream
                                return self._create_tracking_iterator(self._stream)
                            else:
                                # Direct iteration - we need to act as our own context manager
                                return self

                        def __next__(self):
                            # For iterator protocol when used directly
                            if self._iterator is None:
                                # Enter context and start iterating
                                self._stream = self._response.__enter__()
                                self._iterator = self._create_tracking_iterator(
                                    self._stream
                                )
                            try:
                                return next(self._iterator)
                            except StopIteration:
                                # Clean up context when iteration is complete
                                if self._stream is not None:
                                    self._response.__exit__(None, None, None)
                                    self._stream = None
                                    self._iterator = None
                                raise

                        def _create_tracking_iterator(self, stream):
                            for chunk in stream:
                                # Track usage for this chunk
                                payload = self._usage_handler.extract_usage_payload(
                                    chunk,
                                    **self._kw,
                                    attr=self._attr,
                                    base_url=self._base_url,
                                )
                                self._tracker_func(payload)
                                # Call response callback with each chunk
                                self._callback_func(chunk)
                                yield chunk

                    return StreamingWrapper(
                        res,
                        self._track_usage,
                        self._usage_handler,
                        self._call_response_callback,
                        kw,
                        attr,
                        self._base_url,
                    )
                else:
                    # Return a regular generator for non-context manager responses (like completions)
                    def gen():
                        last_chunk = None
                        usage_found = False

                        # Get the correct iterator for streaming (handles Bedrock's special structure)
                        iterator = res
                        if hasattr(self._usage_handler, "get_streaming_iterator"):
                            iterator = self._usage_handler.get_streaming_iterator(
                                res, attr
                            )

                        for chunk in iterator:
                            payload = self._usage_handler.extract_usage_payload(
                                chunk, **kw, attr=attr, base_url=self._base_url
                            )
                            if payload:
                                usage_found = True
                            self._track_usage(payload)
                            last_chunk = chunk

                            # Call response callback with each chunk
                            self._call_response_callback(chunk)

                            yield chunk

                        if last_chunk and not usage_found:
                            payload = self._usage_handler.extract_usage_payload(
                                last_chunk,
                                **kw,
                                attr=attr,
                                base_url=self._base_url,
                            )
                            self._track_usage(payload)

                    return gen()

            payload = self._usage_handler.extract_usage_payload(
                res, **kw, attr=attr, base_url=self._base_url
            )
            self._track_usage(payload)
            return res

        return functools.wraps(attr)(s_wrapper)
