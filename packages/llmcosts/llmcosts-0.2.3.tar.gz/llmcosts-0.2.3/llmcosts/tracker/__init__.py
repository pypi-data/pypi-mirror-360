from .providers import Provider
from .frameworks import Framework
from .proxy import LLMTrackingProxy
from .usage_delivery import (
    UsageTracker,
    get_usage_tracker,
    reset_global_tracker,
)

# Version from package metadata
try:
    from importlib.metadata import version

    __version__ = version("llmcosts")
except ImportError:
    # Fallback for Python < 3.8
    from importlib_metadata import version

    __version__ = version("llmcosts")
except Exception:
    # Ultimate fallback
    __version__ = "0.1.0"

__all__ = [
    "LLMTrackingProxy",
    "Provider",
    "Framework",
    "UsageTracker",
    "get_usage_tracker",
    "reset_global_tracker",
    "__version__",
]
