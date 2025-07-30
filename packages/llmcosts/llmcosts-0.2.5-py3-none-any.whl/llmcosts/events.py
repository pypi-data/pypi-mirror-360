"""Cost event helper functions."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .client import LLMCostsClient


def list_events(
    client: LLMCostsClient,
    start: Optional[str] = None,
    end: Optional[str] = None,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """List or search cost events with filtering by date range, provider, model, and cost thresholds."""
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


def get_event(client: LLMCostsClient, response_id: str) -> Optional[Dict[str, Any]]:
    """Get cost event by response ID."""
    return client.get(f"/event/{response_id}")


def search_events(
    client: LLMCostsClient,
    start: Optional[str] = None,
    end: Optional[str] = None,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Advanced search with aggregations - return aggregated totals grouped by provider and model."""
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
    client: LLMCostsClient,
    format: str = "csv",
    start: Optional[str] = None,
    end: Optional[str] = None,
    provider: Optional[str] = None,
    model_id: Optional[str] = None,
    min_cost: Optional[float] = None,
    max_cost: Optional[float] = None,
) -> str:
    """Export cost events as CSV or JSON using the same filters as /events."""
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

    return client.get("/events/export", params=params)


# Legacy functions for backward compatibility - these don't exist in the API
def create_event(client: LLMCostsClient, data: Dict[str, Any]) -> Any:
    """Legacy function - events are created automatically by usage tracking."""
    raise NotImplementedError(
        "Events are created automatically by usage tracking. Use the tracking proxy instead."
    )


def update_event(client: LLMCostsClient, event_id: str, data: Dict[str, Any]) -> Any:
    """Legacy function - events cannot be updated."""
    raise NotImplementedError(
        "Events cannot be updated. They are immutable records of LLM usage."
    )


def delete_event(client: LLMCostsClient, event_id: str) -> Any:
    """Legacy function - events cannot be deleted."""
    raise NotImplementedError(
        "Events cannot be deleted. They are immutable records of LLM usage."
    )
