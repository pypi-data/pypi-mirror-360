"""
Generic fallback usage handler for unknown LLM providers.
"""

from typing import Any, Dict, Optional

from .base import UsageHandler


class GenericUsageHandler(UsageHandler):
    """Generic handler for non-specific LLM providers."""

    @property
    def provider_name(self) -> str:
        return "Generic"

    def extract_usage_payload(self, obj: Any, attr: Any, **kwargs) -> Optional[Dict]:
        """Extract generic usage payload."""
        usage = None
        if hasattr(obj, "usage"):
            usage = getattr(obj, "usage")
        elif hasattr(obj, "usage_metadata"):
            usage = getattr(obj, "usage_metadata")

        if usage is None:
            return None

        # Convert to dict
        usage_data = (
            usage.model_dump()
            if hasattr(usage, "model_dump")
            else dict(usage)
            if not isinstance(usage, dict)
            else usage
        )

        # Basic payload for non-specific providers
        payload = {"usage": usage_data}

        # Add model if available
        if hasattr(obj, "model") and obj.model is not None:
            payload["model_id"] = obj.model

        return self._add_common_fields(payload, obj)

    def validate_streaming_options(self, target: Any, kw: Dict, attr: Any) -> None:
        """No validation for generic providers."""
        pass

    def is_provider_client(self, target: Any) -> bool:
        """Always returns True as fallback."""
        return True
