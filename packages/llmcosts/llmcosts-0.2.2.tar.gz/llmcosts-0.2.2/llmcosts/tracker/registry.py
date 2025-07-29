"""
Registry for managing LLM provider handlers.
"""

from typing import Any

from .anthropic_handler import AnthropicUsageHandler
from .base import UsageHandler
from .gemini_handler import GeminiUsageHandler
from .bedrock_handler import BedrockUsageHandler
from .generic_handler import GenericUsageHandler
from .openai_handler import OpenAIUsageHandler

# Handler registry - order matters, Generic must be last as fallback
_USAGE_HANDLERS = [
    OpenAIUsageHandler(),
    AnthropicUsageHandler(),
    GeminiUsageHandler(),
    BedrockUsageHandler(),
    GenericUsageHandler(),  # Must be last as fallback
]


def get_usage_handler(target: Any) -> UsageHandler:
    """Get the appropriate usage handler for the target client.

    Args:
        target: The client object to find a handler for

    Returns:
        UsageHandler: The appropriate handler for the target
    """
    for handler in _USAGE_HANDLERS:
        if handler.is_provider_client(target):
            return handler

    # This should never happen since GenericUsageHandler always returns True
    return GenericUsageHandler()


def register_handler(handler: UsageHandler, priority: int = None) -> None:
    """Register a new usage handler.

    Args:
        handler: The usage handler to register
        priority: Position to insert at (default: before generic handler)
    """
    if priority is None:
        # Insert before the generic handler (which should be last)
        priority = len(_USAGE_HANDLERS) - 1

    _USAGE_HANDLERS.insert(priority, handler)


def list_handlers() -> list[UsageHandler]:
    """List all registered handlers.

    Returns:
        List of all registered handlers in priority order
    """
    return _USAGE_HANDLERS.copy()
