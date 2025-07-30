"""Gemini-specific usage handler for Google GenAI models."""

from typing import Any, Dict, Optional

from .base import UsageHandler


class GeminiUsageHandler(UsageHandler):
    """Handler for Google Gemini-specific usage extraction."""

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def is_provider_client(self, target: Any) -> bool:
        """Check if the client is a Gemini client or a sub-client."""
        module_name = getattr(target.__class__, "__module__", "")
        return "google.genai" in module_name

    def extract_usage_payload(
        self, response: Any, attr: Any, **kwargs
    ) -> Optional[Dict]:
        """Extract usage from a Gemini API response or stream chunk."""
        usage_metadata = getattr(response, "usage_metadata", None)

        if not usage_metadata:
            # In some cases (like streaming), usage might be on a candidate
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "usage_metadata"):
                    usage_metadata = candidate.usage_metadata

        if not usage_metadata:
            return None

        # Extract token counts, defaulting to 0 if not present
        usage_dict = {
            "prompt_token_count": getattr(usage_metadata, "prompt_token_count", 0) or 0,
            "candidates_token_count": getattr(
                usage_metadata, "candidates_token_count", 0
            )
            or 0,
            "total_token_count": getattr(usage_metadata, "total_token_count", 0) or 0,
        }

        # Filter out zero-count fields for cleaner logs
        final_usage = {k: v for k, v in usage_dict.items() if v > 0}

        if not final_usage:
            return None

        # The model name is passed from the original call via kwargs
        model_id = kwargs.get("model")

        payload = {
            "model_id": model_id,
            "usage": final_usage,
        }
        return self._add_common_fields(payload, response)

    def validate_streaming_options(self, client: Any, kw: Dict, attr: Any) -> None:
        """No special validation needed for Gemini streaming."""
        pass
