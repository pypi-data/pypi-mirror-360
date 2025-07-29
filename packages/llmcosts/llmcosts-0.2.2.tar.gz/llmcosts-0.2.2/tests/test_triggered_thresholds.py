"""
Test the triggered thresholds functionality in the SDK.

Tests cover:
- LLMCostsClient initialization with triggered thresholds
- Config file storage and loading
- JWT verification (mocked)
- Proxy integration with threshold checking
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from llmcosts.client import LLMCostsClient
from llmcosts.tracker import LLMTrackingProxy, Provider


class TestTriggeredThresholds:
    """Test triggered threshold functionality."""

    def test_client_initialization_with_triggered_thresholds_always_present(self):
        """Test client initialization with triggered thresholds (always present now)."""
        mock_response = {
            "status": "ok",
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "mock-public-key",
                "key_id": "v1",
                "encrypted_payload": "mock-jwt-token",
            },
        }

        with patch.object(LLMCostsClient, "get", return_value=mock_response):
            with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
                client = LLMCostsClient()

                # Should initialize without errors
                assert client.api_key == "test-key"

    def test_client_initialization_with_triggered_thresholds(self):
        """Test client initialization when triggered thresholds are present."""
        mock_response = {
            "status": "ok",
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00Z",
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "mock-public-key",
                "key_id": "v1",
                "encrypted_payload": "mock-jwt-token",
            },
        }

        with patch.object(LLMCostsClient, "get", return_value=mock_response):
            with patch.object(
                LLMCostsClient, "_store_triggered_thresholds"
            ) as mock_store:
                with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
                    client = LLMCostsClient()

                    # Should have called store method
                    mock_store.assert_called_once_with(
                        mock_response["triggered_thresholds"]
                    )

    def test_config_file_storage_and_loading(self):
        """Test storing and loading triggered thresholds config."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.ini"

            triggered_thresholds = {
                "version": "v1.0",
                "public_key": "test-public-key",
                "key_id": "v1",
                "encrypted_payload": "test-jwt-token",
            }

            with patch.dict(
                os.environ,
                {"LLMCOSTS_API_KEY": "test-key", "LLMCOSTS_INI_PATH": str(config_file)},
            ):
                with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                    client = LLMCostsClient()

                    # Store thresholds
                    client._store_triggered_thresholds(triggered_thresholds)

                    # Verify file exists and has correct permissions
                    assert config_file.exists()
                    assert oct(config_file.stat().st_mode)[-3:] == "600"

                    # Load and verify data
                    loaded = client._load_triggered_thresholds()
                    assert loaded is not None
                    assert loaded["version"] == "v1.0"
                    assert loaded["public_key"] == "test-public-key"
                    assert loaded["key_id"] == "v1"
                    assert loaded["encrypted_payload"] == "test-jwt-token"

    def test_jwt_verification_valid(self):
        """Test JWT verification with valid token."""
        mock_payload = {
            "triggered_thresholds": [
                {
                    "event_id": "test-event",
                    "threshold_type": "limit",
                    "amount": "100.00",
                    "period": "monthly",
                    "expires_at": "2024-12-31T23:59:59Z",
                    "triggered_at": "2024-01-01T00:00:00Z",
                }
            ]
        }

        with patch("jwt.decode", return_value=mock_payload):
            with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
                with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                    client = LLMCostsClient()

                    result = client._verify_triggered_threshold_jwt(
                        "mock-token", "mock-key"
                    )
                    assert result == mock_payload

    def test_jwt_verification_expired(self):
        """Test JWT verification with expired token."""
        from jwt import ExpiredSignatureError

        with patch("jwt.decode", side_effect=ExpiredSignatureError):
            with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
                with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                    client = LLMCostsClient()

                    result = client._verify_triggered_threshold_jwt(
                        "expired-token", "mock-key"
                    )
                    assert result is None

    def test_threshold_applies_logic(self):
        """Test the logic for determining if a threshold applies to a request."""
        with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
            with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                client = LLMCostsClient()

                # Test provider-specific threshold
                threshold = {"provider": "openai"}
                assert (
                    client._threshold_applies(threshold, "openai", None, None) is True
                )
                assert (
                    client._threshold_applies(threshold, "anthropic", None, None)
                    is False
                )

                # Test model-specific threshold
                threshold = {"model_id": "gpt-4"}
                assert client._threshold_applies(threshold, None, "gpt-4", None) is True
                assert (
                    client._threshold_applies(threshold, None, "claude-3", None)
                    is False
                )

                # Test client-specific threshold
                threshold = {"client_customer_key": "customer-123"}
                assert (
                    client._threshold_applies(threshold, None, None, "customer-123")
                    is True
                )
                assert (
                    client._threshold_applies(threshold, None, None, "customer-456")
                    is False
                )

                # Test global threshold (no specificity)
                threshold = {}
                assert (
                    client._threshold_applies(
                        threshold, "openai", "gpt-4", "customer-123"
                    )
                    is True
                )

    def test_proxy_threshold_checking_allowed(self):
        """Test proxy allows calls when no thresholds are violated."""
        mock_client = MagicMock()
        mock_client.__class__.__module__ = "openai"
        mock_client.__class__.__name__ = "OpenAI"

        mock_response = MagicMock()
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.id = "test-response"

        mock_client.chat = MagicMock()
        mock_client.chat.completions = MagicMock()
        mock_client.chat.completions.create = MagicMock(return_value=mock_response)

        # Mock threshold check to return allowed
        threshold_result = {
            "status": "checked",
            "allowed": True,
            "violations": [],
            "warnings": [],
        }

        with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
            proxy = LLMTrackingProxy(
                mock_client, provider=Provider.OPENAI, sync_mode=True
            )
            with patch.object(
                proxy._llm_costs_client,
                "check_triggered_thresholds",
                return_value=threshold_result,
            ):
                response = proxy.chat.completions.create(
                    model="gpt-4", messages=[{"role": "user", "content": "Hello"}]
                )

                assert response == mock_response
        mock_client.chat.completions.create.assert_called_once()

    def test_refresh_triggered_thresholds(self):
        """Test manual refresh of triggered thresholds."""
        mock_response = {
            "status": "ok",
            "triggered_thresholds": {
                "version": "v2.0",
                "public_key": "new-public-key",
                "key_id": "v2",
                "encrypted_payload": "new-jwt-token",
            },
        }

        with patch.object(LLMCostsClient, "get", return_value=mock_response):
            with patch.object(
                LLMCostsClient, "_store_triggered_thresholds"
            ) as mock_store:
                with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
                    with patch.object(
                        LLMCostsClient, "_initialize_triggered_thresholds"
                    ):
                        client = LLMCostsClient()

                        result = client.refresh_triggered_thresholds()

                        assert result is True
                        mock_store.assert_called_once_with(
                            mock_response["triggered_thresholds"]
                        )

    def test_config_file_path_env_var(self):
        """Test that LLMCOSTS_INI_PATH environment variable is respected."""
        custom_path = "/custom/path/thresholds.ini"

        with patch.dict(
            os.environ,
            {"LLMCOSTS_API_KEY": "test-key", "LLMCOSTS_INI_PATH": custom_path},
        ):
            with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                client = LLMCostsClient()

                assert str(client._config_file_path) == custom_path

    def test_config_file_path_default(self):
        """Test that default config file path is used when env var is not set."""
        with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}, clear=True):
            with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                client = LLMCostsClient()

                expected_path = Path.home() / ".llmcosts_settings.ini"
                assert client._config_file_path == expected_path

    def test_missing_config_triggers_health_call(self):
        """Test that missing config triggers a health call to prevent threshold avoidance."""
        # Mock health response with triggered thresholds
        mock_health_response = {
            "status": "ok",
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "mock-public-key",
                "key_id": "v1",
                "encrypted_payload": "mock-jwt-token",
            },
        }

        with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
            with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                # Mock that no config exists initially
                with patch.object(
                    LLMCostsClient, "_load_triggered_thresholds", return_value=None
                ):
                    # Mock the health call that should be triggered
                    with patch.object(
                        LLMCostsClient, "get", return_value=mock_health_response
                    ):
                        with patch.object(
                            LLMCostsClient, "_store_triggered_thresholds"
                        ) as mock_store:
                            client = LLMCostsClient()

                            # This should trigger a health call since config is missing
                            result = client.check_triggered_thresholds(
                                provider="openai"
                            )

                            # Should have made a health call and stored the config
                            mock_store.assert_called_once_with(
                                mock_health_response["triggered_thresholds"]
                            )

    def test_api_response_updates_triggered_thresholds(self):
        """Test that triggered thresholds in API responses update the local config."""
        # Mock usage response with updated triggered thresholds
        mock_usage_response = {
            "status": "success",
            "processed": 1,
            "triggered_thresholds": {
                "version": "v2.0",  # Updated version
                "public_key": "new-public-key",
                "key_id": "v2",
                "encrypted_payload": "new-jwt-token",
            },
        }

        with patch.dict(os.environ, {"LLMCOSTS_API_KEY": "test-key"}):
            with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                # Mock current config with older version
                with patch.object(
                    LLMCostsClient,
                    "_load_triggered_thresholds",
                    return_value={"version": "v1.0"},
                ):
                    with patch.object(
                        LLMCostsClient, "_store_triggered_thresholds"
                    ) as mock_store:
                        client = LLMCostsClient()

                        # Simulate the response handling (this happens automatically in post() now)
                        client._handle_triggered_thresholds_in_response(
                            mock_usage_response
                        )

                        # Should have updated the config with new version
                        mock_store.assert_called_once_with(
                            mock_usage_response["triggered_thresholds"]
                        )
