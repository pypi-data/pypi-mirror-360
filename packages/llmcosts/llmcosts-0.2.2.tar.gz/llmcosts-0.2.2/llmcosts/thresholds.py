"""Usage threshold management functions."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .client import LLMCostsClient


def list_thresholds(
    client: LLMCostsClient,
    type: Optional[str] = None,
    client_customer_key: Optional[str] = None,
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
) -> Any:
    """Return alert and limit thresholds associated with the API key."""
    params = {}
    if type is not None:
        params["type"] = type
    if client_customer_key is not None:
        params["client_customer_key"] = client_customer_key
    if model_id is not None:
        params["model_id"] = model_id
    if provider is not None:
        params["provider"] = provider
    response = client.get("/thresholds", params=params)

    # Handle triggered thresholds from response
    if response:
        client._handle_triggered_thresholds_in_response(response)

    return response


def create_threshold(client: LLMCostsClient, data: Dict[str, Any]) -> Any:
    """Create a new usage threshold."""
    response = client.post("/thresholds", json=data)

    # Handle triggered thresholds from response
    if response:
        client._handle_triggered_thresholds_in_response(response)

    return response


def update_threshold(
    client: LLMCostsClient, threshold_id: str, data: Dict[str, Any]
) -> Any:
    """Update an existing usage threshold."""
    response = client.put(f"/thresholds/{threshold_id}", json=data)

    # Handle triggered thresholds from response
    if response:
        client._handle_triggered_thresholds_in_response(response)

    return response


def delete_threshold(client: LLMCostsClient, threshold_id: str) -> Any:
    """Delete a usage threshold."""
    response = client.delete(f"/thresholds/{threshold_id}")

    # Handle triggered thresholds from response
    if response:
        client._handle_triggered_thresholds_in_response(response)

    return response


def list_threshold_events(
    client: LLMCostsClient,
    type: Optional[str] = None,
    client_customer_key: Optional[str] = None,
    model_id: Optional[str] = None,
    provider: Optional[str] = None,
) -> Any:
    """Return active threshold events for the authenticated API key."""
    params = {}
    if type is not None:
        params["type"] = type
    if client_customer_key is not None:
        params["client_customer_key"] = client_customer_key
    if model_id is not None:
        params["model_id"] = model_id
    if provider is not None:
        params["provider"] = provider
    response = client.get("/threshold-events", params=params)

    # Handle triggered thresholds from response
    if response:
        client._handle_triggered_thresholds_in_response(response)

    return response
