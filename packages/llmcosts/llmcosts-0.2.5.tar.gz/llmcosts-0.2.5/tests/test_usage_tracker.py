import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import Mock, patch

import pytest
import requests

from llmcosts.tracker import UsageTracker


class _Handler(BaseHTTPRequestHandler):
    received = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body.decode())
        except Exception:  # pragma: no cover - invalid json
            data = None
        self.received.append(data)
        self.send_response(200)
        self.end_headers()

    def log_message(
        self, *args, **kwargs
    ):  # pragma: no cover - silence default logging
        return


@pytest.fixture
def http_server():
    server = HTTPServer(("localhost", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server, _Handler
    server.shutdown()
    thread.join()


def test_usage_tracker_sends_payload(http_server):
    server, handler = http_server
    handler.received = []
    endpoint = f"http://localhost:{server.server_address[1]}/api/v1/usage"

    # Mock the health check to prevent actual HTTP calls during initialization
    with patch("llmcosts.client.LLMCostsClient.get") as mock_get:
        mock_get.return_value = {}  # No triggered_thresholds
        tracker = UsageTracker(api_endpoint=endpoint, api_key="test-key", batch_size=1)
        tracker.start()

        payload = {
            "model_id": "test-model",
            "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            "response_id": "resp-1",
            "timestamp": "2025-01-01T00:00:00Z",
        }
        tracker.track(payload)
        tracker.shutdown()

        assert handler.received
        # Should send in OpenAPI format: {"usage_records": [...], "remote_save": True}
        expected = {"usage_records": [payload], "remote_save": True}
        assert handler.received[0] == expected


def test_usage_tracker_batches_payloads(http_server):
    server, handler = http_server
    handler.received = []
    endpoint = f"http://localhost:{server.server_address[1]}/api/v1/usage"

    # Mock the health check to prevent actual HTTP calls during initialization
    with patch("llmcosts.client.LLMCostsClient.get") as mock_get:
        mock_get.return_value = {}  # No triggered_thresholds
        tracker = UsageTracker(api_endpoint=endpoint, api_key="test-key", batch_size=2)
        tracker.start()

        tracker.track(
            {
                "model_id": "test-model",
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 2,
                    "total_tokens": 3,
                },
                "response_id": "resp-1",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        )
        tracker.track(
            {
                "model_id": "test-model",
                "usage": {
                    "prompt_tokens": 4,
                    "completion_tokens": 5,
                    "total_tokens": 9,
                },
                "response_id": "resp-2",
                "timestamp": "2025-01-01T00:00:01Z",
            }
        )
        tracker.shutdown()

        assert len(handler.received) == 1
        # Should send in OpenAPI format: {"usage_records": [...], "remote_save": True}
        expected = {
            "usage_records": [
                {
                    "model_id": "test-model",
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 2,
                        "total_tokens": 3,
                    },
                    "response_id": "resp-1",
                    "timestamp": "2025-01-01T00:00:00Z",
                },
                {
                    "model_id": "test-model",
                    "usage": {
                        "prompt_tokens": 4,
                        "completion_tokens": 5,
                        "total_tokens": 9,
                    },
                    "response_id": "resp-2",
                    "timestamp": "2025-01-01T00:00:01Z",
                },
            ],
            "remote_save": True,
        }
        assert handler.received[0] == expected


def test_track_autostarts_worker_when_not_running(http_server):
    server, handler = http_server
    handler.received = []
    endpoint = f"http://localhost:{server.server_address[1]}/api/v1/usage"

    # Mock the health check to prevent actual HTTP calls during initialization
    with patch("llmcosts.client.LLMCostsClient.get") as mock_get:
        mock_get.return_value = {}  # No triggered_thresholds
        tracker = UsageTracker(api_endpoint=endpoint, api_key="test-key", batch_size=1)

        tracker.track(
            {
                "model_id": "test-model",
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
                "response_id": "auto-1",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        )
        assert tracker._worker_thread.is_alive()
        tracker.wait_for_delivery()
        tracker.shutdown()

        assert handler.received
        # Should send in OpenAPI format: {"usage_records": [...], "remote_save": True}
        expected = {
            "usage_records": [
                {
                    "model_id": "test-model",
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                    "response_id": "auto-1",
                    "timestamp": "2025-01-01T00:00:00Z",
                }
            ],
            "remote_save": True,
        }
        assert handler.received[0] == expected


def test_track_sync_mode_does_not_start_worker(http_server):
    server, handler = http_server
    handler.received = []
    endpoint = f"http://localhost:{server.server_address[1]}/api/v1/usage"

    # Mock the health check to prevent actual HTTP calls during initialization
    with patch("llmcosts.client.LLMCostsClient.get") as mock_get:
        mock_get.return_value = {}  # No triggered_thresholds
        tracker = UsageTracker(
            api_endpoint=endpoint, api_key="test-key", batch_size=1, sync_mode=True
        )

        tracker.track(
            {
                "model_id": "test-model",
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
                "response_id": "sync-1",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        )
        assert not tracker._worker_thread.is_alive()
        tracker.shutdown()

        assert handler.received
        # Should send in OpenAPI format: {"usage_records": [...], "remote_save": True}
        expected = {
            "usage_records": [
                {
                    "model_id": "test-model",
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                    "response_id": "sync-1",
                    "timestamp": "2025-01-01T00:00:00Z",
                }
            ],
            "remote_save": True,
        }
        assert handler.received[0] == expected


def test_invalid_model_id_returns_error(monkeypatch):
    """Tracker should record failure for invalid model_id."""
    # Mock the health check to prevent actual HTTP calls during initialization
    with patch("llmcosts.client.LLMCostsClient.get") as mock_get:
        mock_get.return_value = {}  # No triggered_thresholds

        tracker = UsageTracker(
            api_endpoint="http://fake.com/api/v1/usage",
            api_key="k",
            batch_size=1,
            sync_mode=True,
        )

        # Now mock the POST request for the actual tracking call
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 422
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "422 Client Error", response=mock_response
            )
            mock_post.return_value = mock_response

            tracker.track(
                {
                    "model_id": "gpt-4o-mini-invalid",
                    "usage": {
                        "prompt_tokens": 1,
                        "completion_tokens": 1,
                        "total_tokens": 2,
                    },
                    "response_id": "bad-1",
                    "timestamp": "2025-01-01T00:00:00Z",
                }
            )

        assert "422" in tracker.last_error
        assert tracker.stats["total_failed"] == 1
