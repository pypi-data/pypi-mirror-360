"""Public package exports for PyLLMCosts."""

__version__ = "0.2.5"

from .client import LLMCostsClient
from .events import (
    create_event,
    delete_event,
    export_events,
    get_event,
    list_events,
    search_events,
    update_event,
)
from .exceptions import TriggeredLimitError
from .models import (
    calculate_cost_from_tokens,
    calculate_cost_from_usage,
    get_cost_event,
    get_cost_trends,
    get_daily_costs,
    get_model_efficiency,
    get_model_pricing,
    get_model_ranking,
    get_models_by_provider,
    get_models_dict,
    get_monthly_costs,
    get_peak_usage,
    get_provider_comparison,
    get_provider_token_mappings,
    get_providers_by_model,
    get_token_mappings,
    get_usage_frequency,
    get_usage_outliers,
    get_usage_patterns,
    health_check,
    is_model_supported,
    list_models,
)
from .models import (
    list_events as list_cost_events,
)
from .thresholds import (
    create_threshold,
    delete_threshold,
    list_threshold_events,
    list_thresholds,
    update_threshold,
)
from .tracker import (
    Framework,
    LLMTrackingProxy,
    Provider,
    UsageTracker,
    get_usage_tracker,
)

__all__ = [
    "LLMCostsClient",
    "LLMTrackingProxy",
    "Provider",
    "Framework",
    "UsageTracker",
    "get_usage_tracker",
    "TriggeredLimitError",
    "list_thresholds",
    "list_threshold_events",
    "create_threshold",
    "update_threshold",
    "delete_threshold",
    "list_events",
    "get_event",
    "search_events",
    "export_events",
    "create_event",
    "update_event",
    "delete_event",
    "list_models",
    "get_models_dict",
    "get_models_by_provider",
    "get_providers_by_model",
    "is_model_supported",
    "get_model_pricing",
    "get_token_mappings",
    "get_provider_token_mappings",
    "calculate_cost_from_usage",
    "calculate_cost_from_tokens",
    # Health check functions
    "health_check",
    # Events management functions
    "get_cost_event",
    "list_cost_events",
    # Analytics - Cost functions
    "get_daily_costs",
    "get_monthly_costs",
    "get_cost_trends",
    "get_peak_usage",
    # Analytics - Model functions
    "get_model_ranking",
    "get_model_efficiency",
    # Analytics - Provider functions
    "get_provider_comparison",
    # Analytics - Usage functions
    "get_usage_patterns",
    "get_usage_frequency",
    "get_usage_outliers",
]
