"""
OpenAI-specific usage handler for the LLM tracking proxy.

Handles Chat Completions, Legacy Completions, and Responses APIs.
"""

from typing import Any, Dict, Optional

from .base import UsageHandler


class OpenAIUsageHandler(UsageHandler):
    """Handler for OpenAI-specific usage extraction and validation."""

    @property
    def provider_name(self) -> str:
        return "OpenAI"

    def _normalize_model_id(self, model_id: str) -> str:
        """
        Normalize OpenAI model IDs by removing version suffixes that aren't recognized by the server.

        Examples:
        - gpt-4o-mini-2024-07-18 -> gpt-4o-mini
        - gpt-4o-2024-05-13 -> gpt-4o
        - gpt-3.5-turbo-0125 -> gpt-3.5-turbo-0125 (keep this one as server recognizes it)
        """
        if not model_id:
            return model_id

        # Remove common version suffixes for gpt-4o family models
        if model_id.startswith("gpt-4o-mini-"):
            return "gpt-4o-mini"
        elif model_id.startswith("gpt-4o-") and "-20" in model_id:
            return "gpt-4o"
        elif model_id.startswith("gpt-4-turbo-") and "-20" in model_id:
            return "gpt-4-turbo"

        # Keep other model IDs as-is
        return model_id

    def extract_usage_payload(self, obj: Any, attr: Any, **kwargs) -> Optional[Dict]:
        """Extract OpenAI usage payload with model, usage, and service_tier."""
        # The `responses` API sends usage in a final chunk that has a `usage`
        # attribute but no `choices` attribute.
        method_owner = str(getattr(attr, "__self__", ""))
        is_responses_api = "responses" in method_owner
        base_url = kwargs.get("base_url")

        if is_responses_api:
            # For Responses API streaming, usage is nested in obj.response.usage
            if (
                hasattr(obj, "response")
                and hasattr(obj.response, "usage")
                and obj.response.usage is not None
            ):
                usage_data = (
                    obj.response.usage.model_dump()
                    if hasattr(obj.response.usage, "model_dump")
                    else dict(obj.response.usage)
                    if not isinstance(obj.response.usage, dict)
                    else obj.response.usage
                )
                payload = {"usage": usage_data}

                # Model is in obj.response.model
                model = getattr(obj.response, "model", None) or kwargs.get("model")
                if model:
                    payload["model_id"] = self._normalize_model_id(model)

                # Service tier is in obj.response.service_tier
                service_tier = getattr(obj.response, "service_tier", None)
                if service_tier:
                    payload["service_tier"] = service_tier
                return self._add_common_fields(payload, obj)

            # For non-streaming Responses API, usage might be directly on obj
            elif hasattr(obj, "usage"):
                usage_data = obj.usage.model_dump()
                payload = {"usage": usage_data}

                model = getattr(obj, "model", None) or kwargs.get("model")
                if model:
                    payload["model_id"] = self._normalize_model_id(model)

                service_tier = getattr(obj, "service_tier", None)
                if service_tier:
                    payload["service_tier"] = service_tier
                return self._add_common_fields(payload, obj)

        if not hasattr(obj, "usage") or obj.usage is None:
            return None

        # Extract usage data for non-streaming or standard chat completions
        usage_data = (
            obj.usage.model_dump()
            if hasattr(obj.usage, "model_dump")
            else dict(obj.usage)
            if not isinstance(obj.usage, dict)
            else obj.usage
        )

        # Build the payload according to the required schema
        payload = {"usage": usage_data}

        # Add model if available
        if hasattr(obj, "model") and obj.model is not None:
            payload["model_id"] = self._normalize_model_id(obj.model)

        # Add service_tier if available
        if hasattr(obj, "service_tier") and obj.service_tier is not None:
            payload["service_tier"] = obj.service_tier

        if base_url:
            payload["base_url"] = base_url

        return self._add_common_fields(payload, obj)

    def validate_streaming_options(self, target: Any, kw: Dict, attr: Any) -> None:
        """Validate that OpenAI streaming calls include proper stream_options."""
        # This validation only applies to chat.completions and legacy completions
        if "responses" in str(getattr(attr, "__self__", "")):
            return

        if not kw.get("stream"):
            return  # Not streaming, skip validation

        stream_options = kw.get("stream_options", {})
        include_usage = stream_options.get("include_usage", False)

        if not include_usage:
            # Check if auto-injection is enabled (for LangChain compatibility)
            # This is controlled by a flag on the target
            auto_inject = getattr(target, "_auto_inject_stream_options", False)

            if auto_inject:
                # Auto-inject for seamless LangChain integration
                if "stream_options" not in kw:
                    kw["stream_options"] = {}
                kw["stream_options"]["include_usage"] = True
            else:
                # Strict validation for direct OpenAI usage
                raise ValueError(
                    "OpenAI streaming calls require stream_options={'include_usage': True} "
                    "to capture usage information for cost tracking. "
                    "Add stream_options={'include_usage': True} to your streaming call."
                )

    def is_provider_client(self, target: Any) -> bool:
        """Check if the target appears to be an OpenAI client or sub-client."""
        module_name = getattr(target.__class__, "__module__", "").lower()
        if "anthropic" in module_name:
            return False
        if hasattr(target, "_is_anthropic_mock"):
            return False

        # Check if it's from the openai module
        if "openai" in module_name:
            return True

        # Check class name contains openai
        class_name = target.__class__.__name__.lower()
        if "openai" in class_name:
            return True

        # For testing: Check if it's a mock that was set up to look like OpenAI
        if hasattr(target, "_is_openai_mock") and target._is_openai_mock:
            return True

        # Check if it has openai-like structure (chat.completions.create)
        if hasattr(target, "chat") and hasattr(
            getattr(target, "chat", None), "completions"
        ):
            return True

        # Check for legacy completions
        if hasattr(target, "completions"):
            return True

        return False
