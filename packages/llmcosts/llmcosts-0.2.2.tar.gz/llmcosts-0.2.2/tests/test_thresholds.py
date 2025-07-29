from unittest.mock import patch

import pytest

from llmcosts.client import LLMCostsClient
from llmcosts.thresholds import (
    create_threshold,
    delete_threshold,
    list_thresholds,
    update_threshold,
)


class TestThresholdHelpers:
    """Unit tests for threshold management helper functions."""

    @pytest.fixture
    def client(self):
        with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
            yield LLMCostsClient(api_key="test-key", base_url="http://test")

    def test_list_thresholds_builds_params(self, client):
        with patch.object(client, "get", return_value=[]) as mock_get:
            result = list_thresholds(
                client,
                type="alert",
                client_customer_key="cust1",
                model_id="model",
                provider="openai",
            )
            mock_get.assert_called_once_with(
                "/thresholds",
                params={
                    "type": "alert",
                    "client_customer_key": "cust1",
                    "model_id": "model",
                    "provider": "openai",
                },
            )
            assert result == []

    def test_create_threshold_posts_data(self, client):
        payload = {"threshold_type": "alert", "amount": 1, "period": "day"}
        with patch.object(
            client, "post", return_value={"threshold_id": "t1"}
        ) as mock_post:
            result = create_threshold(client, payload)
            mock_post.assert_called_once_with("/thresholds", json=payload)
            assert result == {"threshold_id": "t1"}

    def test_update_threshold_puts_data(self, client):
        payload = {"amount": 2}
        with patch.object(
            client, "put", return_value={"threshold_id": "t1"}
        ) as mock_put:
            result = update_threshold(client, "t1", payload)
            mock_put.assert_called_once_with("/thresholds/t1", json=payload)
            assert result == {"threshold_id": "t1"}

    def test_delete_threshold_calls_delete(self, client):
        with patch.object(
            client, "delete", return_value={"deleted": True}
        ) as mock_delete:
            result = delete_threshold(client, "t1")
            mock_delete.assert_called_once_with("/thresholds/t1")
            assert result == {"deleted": True}

    # New tests to verify triggered_thresholds handling
    def test_list_thresholds_handles_triggered_thresholds(self, client):
        mock_response = {
            "thresholds": [{"id": "t1", "amount": 100}],
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "test-key",
                "key_id": "v1",
                "encrypted_payload": "test-jwt",
            },
        }
        with patch.object(client, "get", return_value=mock_response) as mock_get:
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = list_thresholds(client)

                mock_get.assert_called_once_with("/thresholds", params={})
                mock_handle.assert_called_once_with(mock_response)
                assert result == mock_response

    def test_create_threshold_handles_triggered_thresholds(self, client):
        payload = {"threshold_type": "alert", "amount": 1, "period": "day"}
        mock_response = {
            "threshold_id": "t1",
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "test-key",
                "key_id": "v1",
                "encrypted_payload": "test-jwt",
            },
        }
        with patch.object(client, "post", return_value=mock_response) as mock_post:
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = create_threshold(client, payload)

                mock_post.assert_called_once_with("/thresholds", json=payload)
                mock_handle.assert_called_once_with(mock_response)
                assert result == mock_response

    def test_update_threshold_handles_triggered_thresholds(self, client):
        payload = {"amount": 2}
        mock_response = {
            "threshold_id": "t1",
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "test-key",
                "key_id": "v1",
                "encrypted_payload": "test-jwt",
            },
        }
        with patch.object(client, "put", return_value=mock_response) as mock_put:
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = update_threshold(client, "t1", payload)

                mock_put.assert_called_once_with("/thresholds/t1", json=payload)
                mock_handle.assert_called_once_with(mock_response)
                assert result == mock_response

    def test_delete_threshold_handles_triggered_thresholds(self, client):
        mock_response = {
            "deleted": True,
            "triggered_thresholds": {
                "version": "v1.0",
                "public_key": "test-key",
                "key_id": "v1",
                "encrypted_payload": "test-jwt",
            },
        }
        with patch.object(client, "delete", return_value=mock_response) as mock_delete:
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = delete_threshold(client, "t1")

                mock_delete.assert_called_once_with("/thresholds/t1")
                mock_handle.assert_called_once_with(mock_response)
                assert result == mock_response

    def test_threshold_functions_handle_none_response(self, client):
        """Test that threshold functions handle None responses gracefully."""
        with patch.object(client, "get", return_value=None):
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = list_thresholds(client)

                # Should not call _handle_triggered_thresholds_in_response for None response
                mock_handle.assert_not_called()
                assert result is None

        with patch.object(client, "post", return_value=None):
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = create_threshold(client, {})

                mock_handle.assert_not_called()
                assert result is None

        with patch.object(client, "put", return_value=None):
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = update_threshold(client, "t1", {})

                mock_handle.assert_not_called()
                assert result is None

        with patch.object(client, "delete", return_value=None):
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = delete_threshold(client, "t1")

                mock_handle.assert_not_called()
                assert result is None

    def test_threshold_functions_handle_response_without_triggered_thresholds(
        self, client
    ):
        """Test that threshold functions handle responses that don't have triggered_thresholds."""
        mock_response = {"threshold_id": "t1", "amount": 100}

        with patch.object(client, "get", return_value=mock_response):
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = list_thresholds(client)

                # Should still call _handle_triggered_thresholds_in_response even if no triggered_thresholds
                mock_handle.assert_called_once_with(mock_response)
                assert result == mock_response

    def test_threshold_functions_handle_empty_triggered_thresholds(self, client):
        """Test that threshold functions handle responses with null triggered_thresholds."""
        mock_response = {"threshold_id": "t1", "triggered_thresholds": None}

        with patch.object(client, "post", return_value=mock_response):
            with patch.object(
                client, "_handle_triggered_thresholds_in_response"
            ) as mock_handle:
                result = create_threshold(client, {})

                # Should call _handle_triggered_thresholds_in_response even for null triggered_thresholds
                mock_handle.assert_called_once_with(mock_response)
                assert result == mock_response


class TestThresholdTriggeredThresholdsIntegration:
    """Integration tests for triggered_thresholds handling in threshold operations."""

    @pytest.fixture
    def client_with_temp_config(self):
        """Create a client with a temporary config file for testing."""
        import os
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.ini"

            with patch.dict(os.environ, {"LLMCOSTS_INI_PATH": str(config_file)}):
                with patch.object(LLMCostsClient, "_initialize_triggered_thresholds"):
                    client = LLMCostsClient(api_key="test-key", base_url="http://test")
                    yield client, config_file

    def test_threshold_operations_store_triggered_thresholds_in_ini_file(
        self, client_with_temp_config
    ):
        """Test that threshold operations store triggered_thresholds in the ini file."""
        client, config_file = client_with_temp_config

        triggered_thresholds = {
            "version": "v2.0",
            "public_key": "updated-test-key",
            "key_id": "v2",
            "encrypted_payload": "updated-test-jwt",
        }

        mock_response = {
            "threshold_id": "new-threshold",
            "triggered_thresholds": triggered_thresholds,
        }

        # Test create_threshold stores triggered_thresholds
        with patch.object(client, "post", return_value=mock_response):
            result = create_threshold(client, {"amount": 100})

            # Verify response is returned correctly
            assert result == mock_response

            # Verify triggered_thresholds were stored in ini file
            assert config_file.exists()

            # Load and verify the config
            import configparser

            config = configparser.ConfigParser()
            config.read(config_file)

            assert "triggered_thresholds" in config
            assert config["triggered_thresholds"]["version"] == "v2.0"
            assert config["triggered_thresholds"]["public_key"] == "updated-test-key"
            assert config["triggered_thresholds"]["key_id"] == "v2"
            assert (
                config["triggered_thresholds"]["encrypted_payload"]
                == "updated-test-jwt"
            )
            assert "last_updated" in config["triggered_thresholds"]

    def test_threshold_operations_update_existing_triggered_thresholds(
        self, client_with_temp_config
    ):
        """Test that threshold operations update existing triggered_thresholds."""
        client, config_file = client_with_temp_config

        # First, store some initial triggered_thresholds
        initial_triggered_thresholds = {
            "version": "v1.0",
            "public_key": "initial-key",
            "key_id": "v1",
            "encrypted_payload": "initial-jwt",
        }
        client._store_triggered_thresholds(initial_triggered_thresholds)

        # Now, simulate a threshold operation that returns updated triggered_thresholds
        updated_triggered_thresholds = {
            "version": "v1.1",
            "public_key": "updated-key",
            "key_id": "v1",
            "encrypted_payload": "updated-jwt",
        }

        mock_response = {
            "thresholds": [{"id": "t1"}],
            "triggered_thresholds": updated_triggered_thresholds,
        }

        # Test list_thresholds updates triggered_thresholds
        with patch.object(client, "get", return_value=mock_response):
            result = list_thresholds(client)

            # Verify response is returned correctly
            assert result == mock_response

            # Verify triggered_thresholds were updated in ini file
            import configparser

            config = configparser.ConfigParser()
            config.read(config_file)

            assert config["triggered_thresholds"]["version"] == "v1.1"
            assert config["triggered_thresholds"]["public_key"] == "updated-key"
            assert config["triggered_thresholds"]["encrypted_payload"] == "updated-jwt"

    def test_threshold_operations_clear_triggered_thresholds_when_null(
        self, client_with_temp_config
    ):
        """Test that threshold operations clear triggered_thresholds when response has null."""
        client, config_file = client_with_temp_config

        # First, store some initial triggered_thresholds
        initial_triggered_thresholds = {
            "version": "v1.0",
            "public_key": "initial-key",
            "key_id": "v1",
            "encrypted_payload": "initial-jwt",
        }
        client._store_triggered_thresholds(initial_triggered_thresholds)
        assert config_file.exists()

        # Now, simulate a threshold operation that returns null triggered_thresholds
        mock_response = {
            "threshold_id": "updated-threshold",
            "triggered_thresholds": None,
        }

        # Test update_threshold clears triggered_thresholds
        with patch.object(client, "put", return_value=mock_response):
            result = update_threshold(client, "t1", {"amount": 200})

            # Verify response is returned correctly
            assert result == mock_response

            # Verify triggered_thresholds config file was cleared
            assert not config_file.exists()

    def test_all_threshold_operations_handle_triggered_thresholds_consistently(
        self, client_with_temp_config
    ):
        """Test that all threshold operations handle triggered_thresholds consistently."""
        client, config_file = client_with_temp_config

        triggered_thresholds = {
            "version": "v3.0",
            "public_key": "consistent-test-key",
            "key_id": "v3",
            "encrypted_payload": "consistent-test-jwt",
        }

        # Test each operation type
        operations = [
            ("list_thresholds", lambda: list_thresholds(client), client.get),
            ("create_threshold", lambda: create_threshold(client, {}), client.post),
            (
                "update_threshold",
                lambda: update_threshold(client, "t1", {}),
                client.put,
            ),
            ("delete_threshold", lambda: delete_threshold(client, "t1"), client.delete),
        ]

        for operation_name, operation_func, mock_method in operations:
            # Clear any existing config
            if config_file.exists():
                config_file.unlink()

            mock_response = {
                "operation": operation_name,
                "triggered_thresholds": triggered_thresholds,
            }

            with patch.object(client, mock_method.__name__, return_value=mock_response):
                result = operation_func()

                # Verify response is returned correctly
                assert result == mock_response

                # Verify triggered_thresholds were stored consistently
                assert config_file.exists()

                import configparser

                config = configparser.ConfigParser()
                config.read(config_file)

                assert config["triggered_thresholds"]["version"] == "v3.0"
                assert (
                    config["triggered_thresholds"]["public_key"]
                    == "consistent-test-key"
                )
