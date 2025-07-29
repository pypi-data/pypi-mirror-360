"""
Base classes and interfaces for LLM provider handlers.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

# Compatibility layer for datetime.UTC (introduced in Python 3.11)
try:
    from datetime import UTC
except ImportError:
    # For Python < 3.11, use timezone.utc
    from datetime import timezone

    UTC = timezone.utc


class UsageHandler(ABC):
    """Abstract base class for provider-specific usage handlers."""

    @abstractmethod
    def extract_usage_payload(self, obj: Any, attr: Any, **kwargs) -> Optional[Dict]:
        """Extract usage payload from a response object or chunk.

        Args:
            obj: The response object or streaming chunk.
            attr: The method being called.
            **kwargs: Additional arguments from the original call.

        Returns:
            A dictionary with usage data, or None if not applicable.
        """
        raise NotImplementedError

    def validate_streaming_options(self, target: Any, kw: Dict, attr: Any) -> None:
        """Validate streaming options for the given client and call.

        Args:
            target: The client object.
            kw: The keyword arguments from the call.
            attr: The method being called.
        """
        pass

    def _add_common_fields(self, payload: Dict, obj: Any) -> Dict:
        """Add common fields like response_id and timestamp to the payload."""
        response_id = None
        if hasattr(obj, "id"):
            response_id = getattr(obj, "id")
        elif hasattr(obj, "response") and hasattr(obj.response, "id"):
            response_id = getattr(obj.response, "id")
        elif isinstance(obj, dict):
            response_id = (
                obj.get("id")
                or obj.get("request_id")
                or obj.get("ResponseMetadata", {}).get("RequestId")
            )

        # Generate a unique ID if none was found
        if response_id is None:
            response_id = str(uuid.uuid4())

        payload["response_id"] = response_id
        payload["timestamp"] = datetime.now(UTC).isoformat()
        return payload

    @abstractmethod
    def is_provider_client(self, target: Any) -> bool:
        """Check if target is a client for this provider.

        Args:
            target: The client object to check

        Returns:
            bool: True if this handler should be used for the target
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider's name (e.g., 'OpenAI', 'Anthropic')."""
        raise NotImplementedError
