import pytest
from environs import Env

from llmcosts.client import LLMCostsClient
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

# Load environment variables
env = Env()


class TestTriggeredThresholdsAlwaysPresent:
    """Test that triggered_thresholds are always present in API responses and can be processed."""

    @pytest.fixture
    def api_key(self):
        """Get API key from environment."""
        api_key = env.str("LLMCOSTS_API_KEY", None)
        if not api_key:
            pytest.skip("LLMCOSTS_API_KEY not found in environment")
        return api_key

    def test_health_endpoint_always_has_triggered_thresholds(self, api_key):
        """Test that health endpoint always includes triggered_thresholds field."""
        client = LLMCostsClient(api_key=api_key)

        # Make direct health call
        response = client.get("/health")

        # Should always have triggered_thresholds field (can be null)
        assert "triggered_thresholds" in response, (
            "Health response must always include triggered_thresholds field"
        )

        # The field can be null or a proper object
        triggered_thresholds = response["triggered_thresholds"]
        if triggered_thresholds is not None:
            # If present, should have required fields
            assert "version" in triggered_thresholds
            assert "public_key" in triggered_thresholds
            assert "key_id" in triggered_thresholds
            assert "encrypted_payload" in triggered_thresholds

            print(
                f"✅ Health endpoint returned triggered_thresholds with version: {triggered_thresholds['version']}"
            )
        else:
            print(
                "✅ Health endpoint returned triggered_thresholds as null (no active thresholds)"
            )

    def test_usage_endpoint_always_has_triggered_thresholds(self, api_key):
        """Test that usage endpoint always includes triggered_thresholds field."""
        client = LLMCostsClient(api_key=api_key)

        # Make a usage tracking call
        payload = {
            "usage_records": [
                {
                    "model_id": "gpt-4o-mini",
                    "provider": "openai",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                    "response_id": "test-threshold-check",
                    "timestamp": "2025-01-01T00:00:00Z",
                }
            ],
            "remote_save": False,  # Don't save to avoid cluttering database
        }

        response = client.post("/usage", json=payload)

        # Should always have triggered_thresholds field (can be null)
        assert "triggered_thresholds" in response, (
            "Usage response must always include triggered_thresholds field"
        )

        # The field can be null or a proper object
        triggered_thresholds = response["triggered_thresholds"]
        if triggered_thresholds is not None:
            # If present, should have required fields
            assert "version" in triggered_thresholds
            assert "public_key" in triggered_thresholds
            assert "key_id" in triggered_thresholds
            assert "encrypted_payload" in triggered_thresholds

            print(
                f"✅ Usage endpoint returned triggered_thresholds with version: {triggered_thresholds['version']}"
            )
        else:
            print(
                "✅ Usage endpoint returned triggered_thresholds as null (no active thresholds)"
            )

    def test_client_boolean_properties(self, api_key):
        """Test that LLMCostsClient properly tracks triggered threshold status with boolean properties."""
        client = LLMCostsClient(api_key=api_key)

        # Check that boolean properties are accessible
        has_thresholds = client.has_triggered_thresholds
        version = client.triggered_thresholds_version

        assert isinstance(has_thresholds, bool), (
            "has_triggered_thresholds should be a boolean"
        )

        if has_thresholds:
            assert version is not None, (
                "If has_triggered_thresholds is True, version should not be None"
            )
            assert isinstance(version, str), (
                "triggered_thresholds_version should be a string when present"
            )
            print(f"✅ Client has triggered thresholds with version: {version}")
        else:
            assert version is None, (
                "If has_triggered_thresholds is False, version should be None"
            )
            print("✅ Client has no triggered thresholds")

    def test_triggered_thresholds_decryption(self, api_key):
        """Test that triggered thresholds can be decrypted successfully when present."""
        client = LLMCostsClient(api_key=api_key)

        if client.has_triggered_thresholds:
            # triggered_thresholds should always contain a valid, decryptable JWT
            decrypted = client.get_decrypted_triggered_thresholds()

            assert decrypted is not None, (
                "Should always be able to decrypt triggered thresholds JWT (never invalid)"
            )
            assert isinstance(decrypted, dict), (
                "Decrypted thresholds should be a dictionary"
            )

            # Check expected structure of decrypted payload
            assert "version" in decrypted, "Decrypted payload should have version"
            assert "triggered_thresholds" in decrypted, (
                "Decrypted payload should have triggered_thresholds array"
            )

            triggered_list = decrypted["triggered_thresholds"]
            assert isinstance(triggered_list, list), (
                "triggered_thresholds should be a list (empty if no active thresholds)"
            )

            # Check structure of individual threshold events (if any exist)
            if triggered_list:
                threshold = triggered_list[0]
                expected_fields = [
                    "event_id",
                    "threshold_id",
                    "threshold_type",
                    "amount",
                    "period",
                    "triggered_at",
                ]
                for field in expected_fields:
                    assert field in threshold, (
                        f"Triggered threshold should have {field} field"
                    )

                print(
                    f"✅ Successfully decrypted {len(triggered_list)} triggered threshold(s)"
                )
                print(
                    f"   Sample threshold: {threshold['threshold_type']} - ${threshold['amount']}"
                )
            else:
                print(
                    "✅ Successfully decrypted triggered thresholds (empty list - no active thresholds)"
                )
        else:
            # No triggered thresholds present at all
            decrypted = client.get_decrypted_triggered_thresholds()
            assert decrypted is None, (
                "Should return None when no triggered thresholds present"
            )
            print("✅ No triggered thresholds to decrypt")

    def test_threshold_checking_functionality(self, api_key):
        """Test that threshold checking functionality works correctly."""
        client = LLMCostsClient(api_key=api_key)

        # Test threshold checking with various parameters
        result = client.check_triggered_thresholds(
            provider="openai", model_id="gpt-4o-mini", client_key="test-customer"
        )

        # Should always return a valid result structure
        assert isinstance(result, dict), (
            "check_triggered_thresholds should return a dict"
        )
        assert "status" in result, "Result should have status field"
        assert "allowed" in result, "Result should have allowed field"
        assert "violations" in result, "Result should have violations field"

        assert isinstance(result["allowed"], bool), "allowed field should be boolean"
        assert isinstance(result["violations"], list), "violations field should be list"

        if result["status"] == "checked":
            # If thresholds were checked, should have warnings field
            assert "warnings" in result, "Checked result should have warnings field"
            assert isinstance(result["warnings"], list), "warnings field should be list"

            if result["violations"]:
                print(f"⚠️ Found {len(result['violations'])} threshold violations")
                for violation in result["violations"]:
                    print(f"   - {violation.get('message', 'Unknown violation')}")

            if result["warnings"]:
                print(f"⚠️ Found {len(result['warnings'])} threshold warnings")
                for warning in result["warnings"]:
                    print(f"   - {warning.get('message', 'Unknown warning')}")

            if not result["violations"] and not result["warnings"]:
                print("✅ No threshold violations or warnings")
        else:
            print(f"✅ Threshold check status: {result['status']}")

    def test_proxy_uses_threshold_checking(self, api_key):
        """Test that LLMTrackingProxy properly utilizes threshold checking."""

        # Create a mock client to avoid real API calls
        class MockClient:
            def __init__(self):
                self.__class__.__module__ = "openai"
                self.__class__.__name__ = "OpenAI"

        mock_client = MockClient()

        # Create proxy which should initialize with threshold checking
        proxy = LLMTrackingProxy(mock_client, provider=Provider.OPENAI, api_key=api_key)

        # Verify the proxy has the client for threshold checking
        assert hasattr(proxy, "_llm_costs_client"), (
            "Proxy should have LLMCostsClient for threshold checking"
        )

        client = proxy._llm_costs_client
        assert isinstance(client, LLMCostsClient), (
            "Proxy should have LLMCostsClient instance"
        )

        # Test that client has threshold status
        has_thresholds = client.has_triggered_thresholds
        assert isinstance(has_thresholds, bool), "Client should track threshold status"

        print(
            f"✅ Proxy properly initialized with threshold checking (has_thresholds: {has_thresholds})"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
