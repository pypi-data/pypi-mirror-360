"""Bedrock-specific usage handler for AWS Bedrock models."""

from typing import Any, Dict, Optional

from .base import UsageHandler


class BedrockUsageHandler(UsageHandler):
    """Handler for Amazon Bedrock usage extraction and validation."""

    @property
    def provider_name(self) -> str:
        return "Bedrock"

    def is_provider_client(self, target: Any) -> bool:
        """Detect if the target is a Bedrock client."""
        # Real boto3 clients expose meta.service_model.service_name
        service_name = getattr(
            getattr(target, "meta", None), "service_model", None
        ) and getattr(target.meta.service_model, "service_name", "")
        if isinstance(service_name, str) and "bedrock" in service_name:
            return True
        # Allow tests to mark mock clients
        return bool(getattr(target, "_is_bedrock_mock", False))

    def validate_streaming_options(self, target: Any, kw: Dict, attr: Any) -> None:
        """No special validation for Bedrock streaming."""
        pass

    def get_streaming_iterator(self, response: Any, attr: Any) -> Any:
        """Extract the correct streaming iterator for Bedrock responses.

        Bedrock streaming responses have the structure:
        {
            "ResponseMetadata": {...},
            "stream": EventStream(...)
        }

        We need to iterate over response["stream"], not response itself.
        """
        if isinstance(response, dict) and "stream" in response:
            return response["stream"]
        return response

    def extract_usage_payload(self, obj: Any, attr: Any, **kwargs) -> Optional[Dict]:
        """Extract usage information from Bedrock responses or stream chunks."""
        usage = None
        if isinstance(obj, dict):
            # Check for streaming metadata chunk (contains usage info in streaming responses)
            if "metadata" in obj and isinstance(obj["metadata"], dict):
                usage = obj["metadata"].get("usage")
            # Check for direct usage field (non-streaming responses)
            elif "usage" in obj:
                usage = obj.get("usage")
            # Check for top-level token fields (alternative format)
            elif all(k in obj for k in ("inputTokens", "outputTokens", "totalTokens")):
                usage = {
                    "inputTokens": obj.get("inputTokens", 0),
                    "outputTokens": obj.get("outputTokens", 0),
                    "totalTokens": obj.get("totalTokens", 0),
                }
        # Nothing to report
        if not usage:
            return None

        model = kwargs.get("modelId") or kwargs.get("model") or obj.get("modelId")
        payload = {"usage": usage}
        if model:
            # Send model ID as-is to endpoint (including us. prefix) - server will handle aliasing
            payload["model_id"] = model
        return self._add_common_fields(payload, obj)
