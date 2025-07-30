"""
Anthropic/Claude-specific usage handler for the LLM tracking proxy.

Handles Claude Sonnet 4, Sonnet 3.7, Opus 3, and other Claude models.
"""

from datetime import datetime
from typing import Any, Dict, Optional

# Compatibility layer for datetime.UTC (introduced in Python 3.11)
try:
    from datetime import UTC
except ImportError:
    # For Python < 3.11, use timezone.utc
    from datetime import timezone

    UTC = timezone.utc

from .base import UsageHandler


class AnthropicUsageHandler(UsageHandler):
    """Handler for Anthropic/Claude-specific usage extraction and validation."""

    def __init__(self):
        self._streaming_input_tokens = None
        self._streaming_response_id = None

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    def extract_usage_payload(self, obj: Any, attr: Any, **kwargs) -> Optional[Dict]:
        """Extract Anthropic usage payload with model and usage information."""
        # For streaming, Anthropic sends usage in a 'message_start' event
        # and a final 'message_delta' event. We need to capture both.
        if getattr(obj, "type", "") == "message_start":
            if hasattr(obj, "message") and hasattr(obj.message, "usage"):
                self._streaming_input_tokens = obj.message.usage.input_tokens
            # Capture the response_id from the message_start event
            if hasattr(obj, "message") and hasattr(obj.message, "id"):
                self._streaming_response_id = obj.message.id
            return None  # No final payload until the end

        # Extract usage from the final response or delta chunk
        usage = getattr(obj, "usage", None)
        if usage is None and hasattr(obj, "delta"):  # Final streaming chunk
            usage = getattr(obj.delta, "usage", None)

        if usage is None:
            return None

        # Extract usage data
        usage_data = (
            usage.model_dump()
            if hasattr(usage, "model_dump")
            else dict(usage)
            if not isinstance(usage, dict)
            else usage
        )

        # Filter out null values to prevent server errors
        # The server expects numeric values and fails on null/None
        usage_data = {k: v for k, v in usage_data.items() if v is not None}

        # If we are in a streaming context, merge the input tokens
        if self._streaming_input_tokens is not None:
            usage_data["input_tokens"] = self._streaming_input_tokens
            # Reset for the next call
            self._streaming_input_tokens = None

        # Build the payload according to the required schema
        payload = {"usage": usage_data}

        # Add model if available on the object, otherwise get from kwargs
        model = getattr(obj, "model", None)
        if model is None:
            model = kwargs.get("model")

        if model:
            payload["model_id"] = model

        # Add timestamp
        payload["timestamp"] = self._get_timestamp()

        # For streaming responses, always use the captured response_id if available
        # Don't call _add_common_fields as it might overwrite our captured response_id
        if self._streaming_response_id is not None:
            payload["response_id"] = self._streaming_response_id
            # Reset for the next stream
            self._streaming_response_id = None
        else:
            # For non-streaming responses, use the base class method
            payload = self._add_common_fields(payload, obj)

        return payload

    def validate_streaming_options(self, target: Any, kw: Dict, attr: Any) -> None:
        """Validate Anthropic streaming options.

        Anthropic typically doesn't require special stream_options like OpenAI,
        but we can add validation here if needed in the future.
        """
        # Anthropic streaming generally works without special options
        # No validation needed currently
        pass

    def is_provider_client(self, target: Any) -> bool:
        """Check if the target appears to be an Anthropic client or sub-client."""
        # Check if it's from the anthropic module
        module_name = getattr(target.__class__, "__module__", "")
        if "anthropic" in module_name.lower():
            return True

        # Check class name contains anthropic
        class_name = target.__class__.__name__.lower()
        if "anthropic" in class_name:
            return True

        # Check if it has anthropic-specific attributes
        if hasattr(target, "api_key") and hasattr(target, "_client"):
            # Look for anthropic in the target's attributes
            if hasattr(target, "messages") and not hasattr(target, "chat"):
                # Anthropic uses .messages.create, not .chat.completions.create
                return True

        # For testing: Check if it's a mock that was set up to look like Anthropic
        if hasattr(target, "_is_anthropic_mock") and target._is_anthropic_mock:
            return True

        # Check if it has anthropic-like structure (messages.create)
        if hasattr(target, "messages") and hasattr(
            getattr(target, "messages", None), "create"
        ):
            # But make sure it's not OpenAI (which also has messages)
            if not hasattr(target, "chat"):
                return True

        return False

    def _get_timestamp(self):
        return datetime.now(UTC).isoformat()
