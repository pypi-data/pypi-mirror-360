import os
from unittest.mock import Mock, patch

# Default headers for mocked API calls
API_HEADERS = {"Authorization": "Bearer test-key"}

import pytest
import requests
from environs import Env

# Load env for real endpoint tests
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))


def _build_cost_event(response_id, include_context=False):
    """Build a mock cost event for testing."""
    event = {
        "model_id": "o4-mini",
        "provider": "openai",
        "response_id": response_id,
        "timestamp": "2025-01-01T00:00:00Z",
        "input_tokens": 10,
        "output_tokens": 5,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "input_cost": 0.00001,
        "output_cost": 0.00002,
        "cache_read_cost": 0.0,
        "cache_write_cost": 0.0,
        "total_cost": 0.00003,
        "context": None,
    }
    if include_context:
        event["context"] = {"client": "1234", "user": "abc567"}
    return event


def _mock_response(data):
    mock = Mock()
    mock.status_code = 200
    mock.raise_for_status.return_value = None
    mock.json.return_value = data
    return mock


@patch("requests.get")
@patch("requests.post")
def test_usage_event_default_save(mock_post, mock_get):
    response_id = "resp-1"
    cost_event = _build_cost_event(response_id)
    usage_response = {
        "status": "success",
        "processed": 1,
        "failed": None,
        "errors": None,
        "timestamp": "2025-01-01T00:00:00Z",
        "events": [cost_event],
    }

    mock_post.return_value = _mock_response(usage_response)
    mock_get.return_value = _mock_response(
        cost_event
    )  # Event is retrievable when saved

    payload = {
        "usage_records": [
            {
                "model_id": "o4-mini",
                "provider": "openai",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": response_id,
                "timestamp": "2025-01-01T00:00:00Z",
            }
        ]
        # Default: remote_save=True (when not specified)
    }

    res = requests.post(
        "https://llmcosts.com/api/v1/usage", json=payload, headers=API_HEADERS
    )
    returned_event = res.json()["events"][0]
    assert returned_event == cost_event

    # Event should be retrievable via GET when remote_save=True (default)
    get_res = requests.get(
        f"https://llmcosts.com/api/v1/event/{response_id}", headers=API_HEADERS
    )
    assert get_res.json() == cost_event

    sent_payload = mock_post.call_args[1]["json"]
    assert "remote_save" not in sent_payload  # Default behavior, not specified
    assert sent_payload == payload


@patch("requests.get")
@patch("requests.post")
def test_usage_event_with_context(mock_post, mock_get):
    response_id = "resp-ctx"
    cost_event = _build_cost_event(response_id, include_context=True)
    usage_response = {
        "status": "success",
        "processed": 1,
        "failed": None,
        "errors": None,
        "timestamp": "2025-01-01T00:00:00Z",
        "events": [cost_event],
    }

    mock_post.return_value = _mock_response(usage_response)
    mock_get.return_value = _mock_response(
        cost_event
    )  # Event is retrievable when saved

    payload = {
        "usage_records": [
            {
                "model_id": "o4-mini",
                "provider": "openai",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": response_id,
                "timestamp": "2025-01-01T00:00:00Z",
                "context": {"client": "1234", "user": "abc567"},
            }
        ]
        # Default: remote_save=True (when not specified)
    }

    res = requests.post(
        "https://llmcosts.com/api/v1/usage", json=payload, headers=API_HEADERS
    )
    returned_event = res.json()["events"][0]
    assert returned_event == cost_event

    # Event should be retrievable via GET when remote_save=True (default)
    get_res = requests.get(
        f"https://llmcosts.com/api/v1/event/{response_id}", headers=API_HEADERS
    )
    assert get_res.json() == cost_event

    sent_payload = mock_post.call_args[1]["json"]
    assert "remote_save" not in sent_payload  # Default behavior, not specified
    assert sent_payload == payload


@patch("requests.get")
@patch("requests.post")
def test_usage_event_save_false(mock_post, mock_get):
    response_id = "resp-nosave"
    cost_event = _build_cost_event(response_id)
    usage_response = {
        "status": "success",
        "processed": 1,
        "failed": None,
        "errors": None,
        "timestamp": "2025-01-01T00:00:00Z",
        "events": [cost_event],
    }

    mock_post.return_value = _mock_response(usage_response)
    mock_get.return_value = _mock_response(None)

    payload = {
        "usage_records": [
            {
                "model_id": "o4-mini",
                "provider": "openai",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": response_id,
                "timestamp": "2025-01-01T00:00:00Z",
            }
        ],
        "remote_save": False,
    }

    res = requests.post(
        "https://llmcosts.com/api/v1/usage", json=payload, headers=API_HEADERS
    )
    response_data = res.json()

    # The cost event should be returned in the POST response
    assert "events" in response_data
    assert len(response_data["events"]) > 0
    returned_event = response_data["events"][0]
    assert returned_event == cost_event

    # But the event should not be retrievable via GET
    get_res = requests.get(
        f"https://llmcosts.com/api/v1/event/{response_id}", headers=API_HEADERS
    )
    assert get_res.json() is None

    sent_payload = mock_post.call_args[1]["json"]
    assert sent_payload == payload


class TestLLMCostsEndpointIntegration:
    """Real integration tests that make actual API calls to llmcosts.com"""

    @pytest.fixture
    def api_key(self):
        api_key = env.str("LLMCOSTS_API_KEY", None)
        if not api_key:
            pytest.skip(
                "LLMCOSTS_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API key."
            )
        return api_key

    @pytest.fixture
    def headers(self, api_key):
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def test_usage_event_real_default_save(self, headers):
        """Test posting usage data and retrieving the cost event (real API call)"""
        import datetime
        import uuid

        response_id = f"test-real-{uuid.uuid4()}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "usage_records": [
                {
                    "model_id": "o4-mini",
                    "provider": "openai",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                    "response_id": response_id,
                    "timestamp": timestamp,
                }
            ]
        }

        # Post usage data
        res = requests.post(
            "https://llmcosts.com/api/v1/usage", json=payload, headers=headers
        )
        res.raise_for_status()

        response_data = res.json()
        assert response_data["status"] == "success"
        assert response_data["processed"] == 1
        assert len(response_data["events"]) == 1

        returned_event = response_data["events"][0]
        assert returned_event["response_id"] == response_id
        assert returned_event["model_id"] == "o4-mini"
        assert returned_event["provider"] == "openai"
        assert returned_event["input_tokens"] == 10
        assert returned_event["output_tokens"] == 5

        # Retrieve the event
        get_res = requests.get(
            f"https://llmcosts.com/api/v1/event/{response_id}", headers=headers
        )
        get_res.raise_for_status()

        retrieved_event = get_res.json()
        # Compare core fields - costs may be recalculated dynamically
        assert retrieved_event["response_id"] == response_id
        assert retrieved_event["model_id"] == "o4-mini"
        assert retrieved_event["provider"] == "openai"
        assert retrieved_event["input_tokens"] == 10
        assert retrieved_event["output_tokens"] == 5
        # Verify costs are present and reasonable
        assert retrieved_event["total_cost"] > 0
        assert retrieved_event["input_cost"] > 0
        assert retrieved_event["output_cost"] > 0

    def test_usage_event_real_with_context(self, headers):
        """Test posting usage data with context and retrieving it (real API call)"""
        import datetime
        import uuid

        response_id = f"test-ctx-{uuid.uuid4()}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "usage_records": [
                {
                    "model_id": "gpt-4o-mini",
                    "provider": "openai",
                    "usage": {
                        "prompt_tokens": 15,
                        "completion_tokens": 8,
                        "total_tokens": 23,
                    },
                    "response_id": response_id,
                    "timestamp": timestamp,
                    "context": {"client": "test-client", "user": "test-user"},
                }
            ]
        }

        # Post usage data
        res = requests.post(
            "https://llmcosts.com/api/v1/usage", json=payload, headers=headers
        )
        res.raise_for_status()

        response_data = res.json()
        assert response_data["status"] == "success"
        assert response_data["processed"] == 1

        returned_event = response_data["events"][0]
        assert returned_event["response_id"] == response_id
        assert returned_event["model_id"] == "gpt-4o-mini"
        assert returned_event["context"]["client"] == "test-client"
        assert returned_event["context"]["user"] == "test-user"

        # Retrieve the event
        get_res = requests.get(
            f"https://llmcosts.com/api/v1/event/{response_id}", headers=headers
        )
        get_res.raise_for_status()

        retrieved_event = get_res.json()
        assert retrieved_event["response_id"] == response_id
        assert retrieved_event["model_id"] == "gpt-4o-mini"
        assert retrieved_event["context"]["client"] == "test-client"
        assert retrieved_event["context"]["user"] == "test-user"

    def test_usage_event_real_save_false(self, headers):
        """Test posting usage data with remote_save=False - event should be returned but not saved (real API call)"""
        import datetime
        import uuid

        response_id = f"test-nosave-{uuid.uuid4()}"
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        payload = {
            "usage_records": [
                {
                    "model_id": "gpt-4o-mini",
                    "provider": "openai",
                    "usage": {
                        "prompt_tokens": 8,
                        "completion_tokens": 3,
                        "total_tokens": 11,
                    },
                    "response_id": response_id,
                    "timestamp": timestamp,
                }
            ],
            "remote_save": False,
        }

        # Post usage data
        res = requests.post(
            "https://llmcosts.com/api/v1/usage", json=payload, headers=headers
        )
        res.raise_for_status()

        response_data = res.json()
        assert response_data["status"] == "success"
        assert response_data["processed"] == 1

        # The cost event SHOULD be returned in the response even with remote_save=False
        assert "events" in response_data, (
            "Events should be returned even with remote_save=False"
        )
        assert response_data["events"] is not None, "Events should not be None"
        assert len(response_data["events"]) > 0, "Should have at least one event"

        returned_event = response_data["events"][0]
        assert returned_event["response_id"] == response_id
        assert returned_event["model_id"] == "gpt-4o-mini"
        assert returned_event["provider"] == "openai"
        assert returned_event["input_tokens"] == 8
        assert returned_event["output_tokens"] == 3
        # Verify costs are calculated
        assert returned_event["total_cost"] > 0
        assert returned_event["input_cost"] > 0
        assert returned_event["output_cost"] > 0

        print(
            f"✅ Cost event correctly returned in response: {returned_event['total_cost']}"
        )

        # Now try to retrieve the event - it should NOT be saved to the database
        get_res = requests.get(
            f"https://llmcosts.com/api/v1/event/{response_id}", headers=headers
        )

        # The event should NOT be retrievable because remote_save=False
        assert get_res.status_code == 200, "Expected 200 response"
        retrieved_data = get_res.json()
        assert retrieved_data is None or retrieved_data == {}, (
            f"Event was saved despite remote_save=False: {retrieved_data}"
        )
