"""Models API functions for LLM Costs SDK."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .client import LLMCostsClient
from .tracker import Provider


def list_models(api_key: str = None, base_url: str = None) -> List[Dict[str, Any]]:
    """
    Get JSON list of all available models from the models endpoint.

    This is a direct passthrough to the /api/v1/models endpoint.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of model information dictionaries, each containing:
        - provider: LLM provider name
        - model_id: Model identifier
        - aliases: List of known aliases for the model
        - costs: List of token pricing information (if available)

    Example:
        >>> models = list_models()
        >>> print(f"Found {len(models)} supported models")
        >>> for model in models[:3]:
        ...     print(f"{model['provider']}: {model['model_id']}")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/models")


def get_models_dict(
    api_key: str = None, base_url: str = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get models organized as a dictionary grouped by provider.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary with provider names as keys and lists of model info as values.

    Example:
        >>> models_dict = get_models_dict()
        >>> print(f"OpenAI models: {len(models_dict.get('openai', []))}")
        >>> for model in models_dict.get('anthropic', []):
        ...     print(f"Anthropic: {model['model_id']}")
    """
    models = list_models(api_key=api_key, base_url=base_url)
    result = {}
    for model in models:
        provider = model["provider"]
        if provider not in result:
            result[provider] = []
        result[provider].append(model)
    return result


def get_models_by_provider(
    provider: Union[Provider, str], api_key: str = None, base_url: str = None
) -> List[str]:
    """
    Get list of all model IDs supported by a specific provider.

    Args:
        provider: Provider enum value or string name (e.g., Provider.OPENAI or 'openai')
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of model IDs for the specified provider.

    Example:
        >>> from llmcosts import Provider
        >>> openai_models = get_models_by_provider(Provider.OPENAI)
        >>> print(f"OpenAI supports {len(openai_models)} models")
        >>> print(openai_models[:3])  # Show first 3

        >>> # Or use string
        >>> anthropic_models = get_models_by_provider('anthropic')
    """
    # Convert Provider enum to string if needed
    if isinstance(provider, Provider):
        provider_str = provider.value
    else:
        provider_str = str(provider).lower()

    models = list_models(api_key=api_key, base_url=base_url)
    return [
        model["model_id"]
        for model in models
        if model["provider"].lower() == provider_str
    ]


def get_providers_by_model(
    model_id: str, api_key: str = None, base_url: str = None
) -> List[str]:
    """
    Get list of all providers that support a specific model ID or alias.

    Args:
        model_id: Model ID or alias to search for
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of provider names that support the model.

    Example:
        >>> providers = get_providers_by_model('gpt-4')
        >>> print(f"GPT-4 is supported by: {', '.join(providers)}")

        >>> # Check by alias
        >>> providers = get_providers_by_model('claude-sonnet')
    """
    models = list_models(api_key=api_key, base_url=base_url)
    providers = []

    for model in models:
        # Check exact model_id match
        if model["model_id"] == model_id:
            providers.append(model["provider"])
        # Check aliases
        elif model_id in model.get("aliases", []):
            providers.append(model["provider"])

    return list(set(providers))  # Remove duplicates


def is_model_supported(
    provider: Union[Provider, str],
    model_id: str,
    api_key: str = None,
    base_url: str = None,
) -> bool:
    """
    Check if a specific provider/model combination is supported.

    Args:
        provider: Provider enum value or string name
        model_id: Model ID or alias to check
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        True if the provider supports the model, False otherwise.

    Example:
        >>> from llmcosts import Provider
        >>> if is_model_supported(Provider.OPENAI, 'gpt-4'):
        ...     print("OpenAI supports GPT-4")

        >>> # Check with string provider
        >>> if is_model_supported('anthropic', 'claude-3-sonnet'):
        ...     print("Anthropic supports Claude 3 Sonnet")

        >>> # Check with alias
        >>> supported = is_model_supported('openai', 'gpt-4-turbo')
    """
    # Convert Provider enum to string if needed
    if isinstance(provider, Provider):
        provider_str = provider.value
    else:
        provider_str = str(provider).lower()

    models = list_models(api_key=api_key, base_url=base_url)

    for model in models:
        if model["provider"].lower() == provider_str:
            # Check exact model_id match
            if model["model_id"] == model_id:
                return True
            # Check aliases
            if model_id in model.get("aliases", []):
                return True

    return False


def get_model_pricing(
    provider: Union[Provider, str],
    model_id: str,
    api_key: str = None,
    base_url: str = None,
) -> Optional[Dict[str, Any]]:
    """
    Get pricing information for a specific provider/model combination.

    Args:
        provider: Provider enum value or string name (e.g., Provider.OPENAI or 'openai')
        model_id: Model ID to get pricing for
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary containing pricing information with:
        - provider: Provider name
        - model_id: Model identifier
        - costs: List of token costs with token_type and cost_per_million
        - aliases: List of known aliases
        Returns None if model not found.

    Example:
        >>> pricing = get_model_pricing(Provider.OPENAI, "gpt-4o-mini")
        >>> if pricing:
        ...     for cost in pricing['costs']:
        ...         print(f"{cost['token_type']}: ${cost['cost_per_million']}/M tokens")
        >>>
        >>> # Works with aliases too
        >>> pricing = get_model_pricing("anthropic", "claude-3-sonnet")
    """
    # Convert Provider enum to string if needed
    if isinstance(provider, Provider):
        provider_str = provider.value
    else:
        provider_str = str(provider).lower()

    models = list_models(api_key=api_key, base_url=base_url)

    for model in models:
        if model["provider"].lower() == provider_str:
            # Check exact model_id match
            if model["model_id"] == model_id:
                return model
            # Check aliases
            if model_id in model.get("aliases", []):
                return model

    return None


def get_token_mappings(
    provider: Optional[Union[Provider, str]] = None,
    include_examples: bool = False,
    api_key: str = None,
    base_url: str = None,
) -> Dict[str, Any]:
    """
    Get token name mappings for all providers or a specific provider.

    Shows how provider-specific token names map to normalized categories.

    Args:
        provider: Optional provider to filter by. If None, returns mappings for all providers.
        include_examples: Whether to include normalization examples
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary containing:
        - provider: Provider name (null for all providers)
        - token_mappings: List of token type mappings
        - special_handling: Provider-specific special handling info
        - examples: Examples of normalization (if include_examples=True)
        - supported_providers: List of all supported providers

    Example:
        >>> mappings = get_token_mappings()
        >>> print(f"Supported providers: {mappings['supported_providers']}")
        >>>
        >>> # Get mappings for specific provider with examples
        >>> openai_mappings = get_token_mappings(Provider.OPENAI, include_examples=True)
        >>> for mapping in openai_mappings['token_mappings']:
        ...     print(f"{mapping['normalized_name']}: {mapping['provider_aliases']}")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {}
    if provider is not None:
        # Convert Provider enum to string if needed
        if isinstance(provider, Provider):
            params["provider"] = provider.value
        else:
            params["provider"] = str(provider).lower()

    if include_examples:
        params["include_examples"] = True

    return client.get("/token-mappings", params=params)


def get_provider_token_mappings(
    provider: Union[Provider, str], api_key: str = None, base_url: str = None
) -> Dict[str, Any]:
    """
    Get token mappings for a specific provider with normalization examples.

    Args:
        provider: Provider enum value or string name
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary containing provider-specific token mappings with examples.
        Returns 404 error if provider not found.

    Example:
        >>> mappings = get_provider_token_mappings(Provider.OPENAI)
        >>> for example in mappings['examples']:
        ...     print(f"Raw: {example['raw_usage']}")
        ...     print(f"Normalized: {example['normalized_tokens']}")
        ...     print(f"Explanation: {example['explanation']}")
    """
    # Convert Provider enum to string if needed
    if isinstance(provider, Provider):
        provider_str = provider.value
    else:
        provider_str = str(provider).lower()

    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get(f"/token-mappings/{provider_str}")


def calculate_cost_from_usage(
    provider: Union[Provider, str],
    model_id: str,
    usage: Dict[str, Any],
    include_explanation: bool = False,
    api_key: str = None,
    base_url: str = None,
) -> Dict[str, Any]:
    """
    Calculate costs given a usage element from a provider LLM call.

    This function normalizes provider-specific usage data and calculates costs
    using the provider's billing logic.

    Args:
        provider: Provider enum value or string name
        model_id: Model identifier
        usage: Provider-specific usage data (e.g., from response.usage)
        include_explanation: Whether to include detailed billing explanations
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary containing:
        - provider: Provider name
        - model_id: Model identifier
        - model_found: Whether pricing was found for this model
        - tokens: Normalized token counts used for calculation
        - costs: Calculated costs by token type
        - billing_model: Billing model used
        - explanations: Detailed billing explanations (if requested)
        - warnings: Any warnings about the calculation

    Example:
        >>> # From OpenAI response
        >>> usage_data = {
        ...     "prompt_tokens": 100,
        ...     "completion_tokens": 50,
        ...     "total_tokens": 150
        ... }
        >>> cost_result = calculate_cost_from_usage(
        ...     Provider.OPENAI, "gpt-4o-mini", usage_data, include_explanation=True
        ... )
        >>> print(f"Total cost: ${cost_result['costs']['total_cost']}")
        >>> for explanation in cost_result.get('explanations', []):
        ...     print(f"{explanation['token_type']}: {explanation['formula']}")
    """
    # Convert Provider enum to string if needed
    if isinstance(provider, Provider):
        provider_str = provider.value
    else:
        provider_str = str(provider).lower()

    # Normalize the usage data based on provider type
    normalized_tokens = {
        "input": 0,
        "output": 0,
        "cache_read": 0,
        "cache_write": 0,
        "reasoning": 0,
        "tool_use": 0,
        "connector": 0,
        "thoughts": 0,
    }

    # Map provider-specific token names to normalized names
    if provider_str == "openai":
        normalized_tokens["input"] = usage.get("prompt_tokens", 0)
        normalized_tokens["output"] = usage.get("completion_tokens", 0)
        normalized_tokens["cache_read"] = usage.get("cache_read_tokens", 0)
        normalized_tokens["cache_write"] = usage.get("cache_write_tokens", 0)
        normalized_tokens["reasoning"] = usage.get("reasoning_tokens", 0)
        normalized_tokens["tool_use"] = usage.get("tool_use_tokens", 0)
    elif provider_str == "anthropic":
        normalized_tokens["input"] = usage.get("input_tokens", 0)
        normalized_tokens["output"] = usage.get("output_tokens", 0)
        normalized_tokens["cache_read"] = usage.get("cache_read_tokens", 0)
        normalized_tokens["cache_write"] = usage.get("cache_write_tokens", 0)
    else:
        # For other providers, try common mappings
        normalized_tokens["input"] = usage.get(
            "input_tokens", usage.get("prompt_tokens", 0)
        )
        normalized_tokens["output"] = usage.get(
            "output_tokens", usage.get("completion_tokens", 0)
        )
        for key in [
            "cache_read_tokens",
            "cache_write_tokens",
            "reasoning_tokens",
            "tool_use_tokens",
            "connector_tokens",
            "thoughts_tokens",
        ]:
            normalized_key = key.replace("_tokens", "")
            normalized_tokens[normalized_key] = usage.get(key, 0)

    # Use the normalized token calculation
    return calculate_cost_from_tokens(
        provider=provider_str,
        model_id=model_id,
        input_tokens=normalized_tokens["input"],
        output_tokens=normalized_tokens["output"],
        cache_read_tokens=normalized_tokens["cache_read"],
        cache_write_tokens=normalized_tokens["cache_write"],
        reasoning_tokens=normalized_tokens["reasoning"],
        tool_use_tokens=normalized_tokens["tool_use"],
        connector_tokens=normalized_tokens["connector"],
        thoughts_tokens=normalized_tokens["thoughts"],
        include_explanation=include_explanation,
        api_key=api_key,
        base_url=base_url,
    )


def calculate_cost_from_tokens(
    provider: Union[Provider, str],
    model_id: str,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
    reasoning_tokens: int = 0,
    tool_use_tokens: int = 0,
    connector_tokens: int = 0,
    thoughts_tokens: int = 0,
    include_explanation: bool = False,
    api_key: str = None,
    base_url: str = None,
) -> Dict[str, Any]:
    """
    Calculate costs given normalized token counts and provider/model.

    Args:
        provider: Provider enum value or string name
        model_id: Model identifier
        input_tokens: Input/prompt tokens (default: 0)
        output_tokens: Output/completion tokens (default: 0)
        cache_read_tokens: Tokens read from cache (default: 0)
        cache_write_tokens: Tokens written to cache (default: 0)
        reasoning_tokens: Reasoning tokens for o1 models (default: 0)
        tool_use_tokens: Tool/function call tokens (default: 0)
        connector_tokens: External connector tokens (default: 0)
        thoughts_tokens: Internal thinking tokens (default: 0)
        include_explanation: Whether to include detailed billing explanations
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary containing calculated costs and breakdown by token type.

    Example:
        >>> cost_result = calculate_cost_from_tokens(
        ...     Provider.OPENAI, "gpt-4o-mini",
        ...     input_tokens=1000, output_tokens=500,
        ...     include_explanation=True
        ... )
        >>> print(f"Input cost: ${cost_result['costs']['input_cost']}")
        >>> print(f"Output cost: ${cost_result['costs']['output_cost']}")
        >>> print(f"Total cost: ${cost_result['costs']['total_cost']}")
    """
    # Convert Provider enum to string if needed
    if isinstance(provider, Provider):
        provider_str = provider.value
    else:
        provider_str = str(provider).lower()

    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    tokens = {
        "input": input_tokens,
        "output": output_tokens,
        "cache_read": cache_read_tokens,
        "cache_write": cache_write_tokens,
        "reasoning": reasoning_tokens,
        "tool_use": tool_use_tokens,
        "connector": connector_tokens,
        "thoughts": thoughts_tokens,
    }

    payload = {
        "provider": provider_str,
        "model_id": model_id,
        "tokens": tokens,
        "include_explanation": include_explanation,
    }

    return client.post("/calculate-costs", json=payload)


# =============================================================================
# Health Check Functions
# =============================================================================


def health_check(api_key: str = None, base_url: str = None) -> Dict[str, Any]:
    """
    Check API health status.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Dictionary containing:
        - status: API health status
        - version: API version
        - timestamp: Current timestamp

    Example:
        >>> health = health_check()
        >>> print(f"API Status: {health['status']}")
        >>> print(f"Version: {health['version']}")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/health")


# =============================================================================
# Events Management Functions
# =============================================================================


def get_cost_event(
    response_id: str, api_key: str = None, base_url: str = None
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a cost event by response ID.

    Args:
        response_id: The response ID to look up
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        CostSummary dictionary or None if not found

    Example:
        >>> event = get_cost_event("chatcmpl-123abc")
        >>> if event:
        ...     print(f"Total cost: ${event['total_cost']}")
        ...     print(f"Model: {event['model_id']}")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get(f"/event/{response_id}")


def list_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    api_key: str = None,
    base_url: str = None,
) -> List[Dict[str, Any]]:
    """
    List or search cost events with filtering.

    Args:
        start: Start date for filtering (ISO format)
        end: End date for filtering (ISO format)
        provider: Filter by provider name
        model_id: Filter by model ID
        min_cost: Minimum cost threshold
        max_cost: Maximum cost threshold
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of CostEventData dictionaries

    Example:
        >>> # Get all events from the last 7 days
        >>> from datetime import datetime, timedelta
        >>> start_date = (datetime.now() - timedelta(days=7)).isoformat()
        >>> events = list_events(start=start_date, provider="openai")
        >>> print(f"Found {len(events)} OpenAI events in the last 7 days")

        >>> # Get high-cost events
        >>> expensive_events = list_events(min_cost=0.01)  # > $0.01
        >>> for event in expensive_events:
        ...     print(f"{event['model_id']}: ${event['total_cost']}")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    if provider is not None:
        params["provider"] = provider
    if model_id is not None:
        params["model_id"] = model_id
    if min_cost is not None:
        params["min_cost"] = min_cost
    if max_cost is not None:
        params["max_cost"] = max_cost

    return client.get("/events", params=params)


def search_events(
    start: Optional[str] = None,
    end: Optional[str] = None,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    api_key: str = None,
    base_url: str = None,
) -> List[Dict[str, Any]]:
    """
    Advanced search with aggregations grouped by provider and model.

    Args:
        start: Start date for filtering (ISO format)
        end: End date for filtering (ISO format)
        provider: Filter by provider name
        model_id: Filter by model ID
        min_cost: Minimum cost threshold
        max_cost: Maximum cost threshold
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of EventAggregateItem dictionaries with aggregated totals

    Example:
        >>> # Get aggregated costs by provider/model
        >>> aggregates = search_events(provider="openai")
        >>> for agg in aggregates:
        ...     print(f"{agg['provider']} {agg['model_id']}: ${agg['total_cost']} ({agg['call_count']} calls)")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    if provider is not None:
        params["provider"] = provider
    if model_id is not None:
        params["model_id"] = model_id
    if min_cost is not None:
        params["min_cost"] = min_cost
    if max_cost is not None:
        params["max_cost"] = max_cost

    return client.get("/events/search", params=params)


def export_events(
    format: str = "csv",
    start: Optional[str] = None,
    end: Optional[str] = None,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
    api_key: str = None,
    base_url: str = None,
) -> str:
    """
    Export cost events as CSV or JSON using the same filters as list_events.

    Args:
        format: Export format ("csv" or "json")
        start: Start date for filtering (ISO format)
        end: End date for filtering (ISO format)
        provider: Filter by provider name
        model_id: Filter by model ID
        min_cost: Minimum cost threshold
        max_cost: Maximum cost threshold
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        Exported data as a string (CSV or JSON format)

    Example:
        >>> # Export all OpenAI events as CSV
        >>> csv_data = export_events(format="csv", provider="openai")
        >>> with open("openai_events.csv", "w") as f:
        ...     f.write(csv_data)

        >>> # Export high-cost events as JSON
        >>> json_data = export_events(format="json", min_cost=0.01)
        >>> with open("expensive_events.json", "w") as f:
        ...     f.write(json_data)
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {"format": format}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    if provider is not None:
        params["provider"] = provider
    if model_id is not None:
        params["model_id"] = model_id
    if min_cost is not None:
        params["min_cost"] = min_cost
    if max_cost is not None:
        params["max_cost"] = max_cost

    # For export functions, we want the raw response text, not parsed JSON
    response = client.session.get(client._url("/events/export"), params=params)
    response.raise_for_status()
    return response.text


# =============================================================================
# Analytics Functions - Cost Analytics
# =============================================================================


def get_daily_costs(
    start: Optional[str] = None,
    end: Optional[str] = None,
    api_key: str = None,
    base_url: str = None,
) -> List[Dict[str, Any]]:
    """
    Get daily cost breakdown between start and end dates.

    Args:
        start: Start date (ISO format)
        end: End date (ISO format)
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of DailyCostItem dictionaries containing date, total_cost, call_count

    Example:
        >>> # Get costs for the last 30 days
        >>> from datetime import datetime, timedelta
        >>> end_date = datetime.now().isoformat()
        >>> start_date = (datetime.now() - timedelta(days=30)).isoformat()
        >>> daily_costs = get_daily_costs(start=start_date, end=end_date)
        >>> for day in daily_costs:
        ...     print(f"{day['date']}: ${day['total_cost']:.4f} ({day['call_count']} calls)")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end

    return client.get("/analytics/costs/daily", params=params)


def get_monthly_costs(
    year: Optional[int] = None,
    api_key: str = None,
    base_url: str = None,
) -> List[Dict[str, Any]]:
    """
    Get monthly cost summaries for a given year.

    Args:
        year: Year to get monthly costs for (default: current year)
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of MonthlyCostItem dictionaries containing month, total_cost, call_count

    Example:
        >>> # Get monthly costs for 2024
        >>> monthly_costs = get_monthly_costs(year=2024)
        >>> for month in monthly_costs:
        ...     print(f"{month['month']}: ${month['total_cost']:.2f} ({month['call_count']} calls)")

        >>> # Get current year costs
        >>> current_costs = get_monthly_costs()
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {}
    if year is not None:
        params["year"] = year

    return client.get("/analytics/costs/monthly", params=params)


def get_cost_trends(
    period: str = "7d",
    api_key: str = None,
    base_url: str = None,
) -> List[Dict[str, Any]]:
    """
    Get cost trends over time periods.

    Args:
        period: Time period ("24h", "7d", "mtd", "ytd")
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of TrendItem dictionaries containing label, cost, count

    Example:
        >>> # Get 7-day trend
        >>> trends = get_cost_trends(period="7d")
        >>> for trend in trends:
        ...     print(f"{trend['label']}: ${trend['cost']:.4f} ({trend['count']} calls)")

        >>> # Get year-to-date trend
        >>> ytd_trends = get_cost_trends(period="ytd")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {"period": period}

    return client.get("/analytics/costs/trends", params=params)


def get_peak_usage(
    days: int = 30,
    api_key: str = None,
    base_url: str = None,
) -> Optional[Dict[str, Any]]:
    """
    Identify peak usage periods within a given time window.

    Args:
        days: Number of days to look back (default: 30)
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        PeakUsageItem dictionary with timestamp, total_cost, call_count or None if no data

    Example:
        >>> # Find peak usage in last 30 days
        >>> peak = get_peak_usage(days=30)
        >>> if peak:
        ...     print(f"Peak usage on {peak['timestamp']}")
        ...     print(f"Cost: ${peak['total_cost']:.4f}")
        ...     print(f"Calls: {peak['call_count']}")

        >>> # Find peak usage in last week
        >>> week_peak = get_peak_usage(days=7)
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)

    params = {"days": days}

    return client.get("/analytics/costs/peak-usage", params=params)


# =============================================================================
# Analytics Functions - Model Analytics
# =============================================================================


def get_model_ranking(
    api_key: str = None, base_url: str = None
) -> List[Dict[str, Any]]:
    """
    Get models ranked by total cost and usage.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of ModelRankingItem dictionaries ranked by cost

    Example:
        >>> rankings = get_model_ranking()
        >>> print("Top models by cost:")
        >>> for i, model in enumerate(rankings[:5], 1):
        ...     print(f"{i}. {model['provider']} {model['model_id']}: ${model['total_cost']:.4f}")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/analytics/models/ranking")


def get_model_efficiency(
    api_key: str = None, base_url: str = None
) -> List[Dict[str, Any]]:
    """
    Get model efficiency metrics (cost per token ratios).

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of ModelEfficiencyItem dictionaries with efficiency metrics

    Example:
        >>> efficiency = get_model_efficiency()
        >>> print("Most efficient models (lowest cost per token):")
        >>> sorted_models = sorted(efficiency, key=lambda x: x['cost_per_token'])
        >>> for model in sorted_models[:5]:
        ...     print(f"{model['provider']} {model['model_id']}: ${model['cost_per_token']:.6f}/token")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/analytics/models/efficiency")


# =============================================================================
# Analytics Functions - Provider Analytics
# =============================================================================


def get_provider_comparison(
    api_key: str = None, base_url: str = None
) -> List[Dict[str, Any]]:
    """
    Compare costs between providers.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of ProviderComparisonItem dictionaries with provider comparisons

    Example:
        >>> comparison = get_provider_comparison()
        >>> print("Provider cost comparison:")
        >>> for provider in comparison:
        ...     avg_cost = provider['total_cost'] / provider['call_count'] if provider['call_count'] > 0 else 0
        ...     print(f"{provider['provider']}: ${provider['total_cost']:.4f} total, ${avg_cost:.6f} avg/call")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/analytics/providers/comparison")


# =============================================================================
# Analytics Functions - Usage Analytics
# =============================================================================


def get_usage_patterns(api_key: str = None, base_url: str = None) -> Dict[str, Any]:
    """
    Get usage patterns by hour of day and day of week.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        UsagePatternResponse dictionary with hourly and weekday patterns

    Example:
        >>> patterns = get_usage_patterns()
        >>> print("Usage by hour of day:")
        >>> for hour in patterns['hourly']:
        ...     print(f"Hour {hour['label']}: {hour['call_count']} calls")
        >>>
        >>> print("\\nUsage by day of week:")
        >>> for day in patterns['weekday']:
        ...     print(f"{day['label']}: {day['call_count']} calls")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/analytics/usage/patterns")


def get_usage_frequency(
    api_key: str = None, base_url: str = None
) -> List[Dict[str, Any]]:
    """
    Get usage frequency by day.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of FrequencyItem dictionaries with daily frequency data

    Example:
        >>> frequency = get_usage_frequency()
        >>> print("Daily usage frequency:")
        >>> for day in frequency[-7:]:  # Last 7 days
        ...     print(f"{day['date']}: {day['call_count']} calls")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/analytics/usage/frequency")


def get_usage_outliers(
    api_key: str = None, base_url: str = None
) -> List[Dict[str, Any]]:
    """
    Identify unusual usage spikes.

    Args:
        api_key: API key for authentication. If not provided, will use LLMCOSTS_API_KEY env var.
        base_url: Base URL for the API. If not provided, will use LLMCOSTS_BASE_URL env var or default.

    Returns:
        List of OutlierItem dictionaries with outlier information

    Example:
        >>> outliers = get_usage_outliers()
        >>> if outliers:
        ...     print("Usage outliers detected:")
        ...     for outlier in outliers:
        ...         print(f"{outlier['date']}: {outlier['call_count']} calls, ${outlier['total_cost']:.4f}")
        ... else:
        ...     print("No usage outliers detected")
    """
    client = LLMCostsClient(api_key=api_key, base_url=base_url)
    return client.get("/analytics/usage/outliers")
