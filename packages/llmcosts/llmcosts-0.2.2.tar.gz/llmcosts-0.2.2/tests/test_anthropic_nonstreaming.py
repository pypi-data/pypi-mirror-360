"""
Dedicated tests for Anthropic non-streaming usage tracking and cost event integration.

Focus: Non-streaming Anthropic Claude API calls (messages.create).
"""

import json
import os
from unittest.mock import MagicMock, Mock

import pytest
from environs import Env

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

# Load environment variables
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))

# Attempt to import anthropic
try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Skip all tests if anthropic is not available
pytestmark = pytest.mark.skipif(
    not ANTHROPIC_AVAILABLE, reason="anthropic library not installed"
)

# Test models - latest Claude models
CLAUDE_MODELS = [
    "claude-sonnet-4-20250514",
    "claude-3-7-sonnet-20250219",
    "claude-3-5-haiku-20241022",
]


class TestAnthropicNonStreaming:
    """Test non-streaming Anthropic Claude API calls."""

    @pytest.fixture
    def anthropic_client(self):
        """Create an Anthropic client wrapped with tracking proxy."""
        api_key = env.str("ANTHROPIC_API_KEY", None)
        if not api_key:
            pytest.skip(
                "ANTHROPIC_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )

        client = anthropic.Anthropic(api_key=api_key)
        return LLMTrackingProxy(client, provider=Provider.ANTHROPIC, debug=True)

    @pytest.mark.parametrize("model", CLAUDE_MODELS)
    def test_messages_create_non_streaming(self, anthropic_client, model, caplog):
        """Test non-streaming messages.create with various Claude models."""
        response = anthropic_client.messages.create(
            model=model,
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": "What is the capital of France? Answer in one word.",
                }
            ],
        )

        # Verify response structure
        assert hasattr(response, "content")
        assert len(response.content) > 0
        assert response.content[0].text

        # Check that usage information was captured and printed
        assert "[LLM costs] Anthropic usage →" in caplog.text

        # Parse the printed JSON to verify structure
        usage_line = [
            line for line in caplog.text.split("\n") if "Anthropic usage →" in line
        ][0]
        usage_json_str = usage_line.split("Anthropic usage → ")[1]
        usage_data = json.loads(usage_json_str)
        assert "response_id" in usage_data
        assert "timestamp" in usage_data

        # Verify required fields
        assert "usage" in usage_data
        assert "model_id" in usage_data
        # Loosen assertion to handle API returning full model name for aliases
        returned_model = usage_data["model_id"]
        if "latest" in model:
            base_model = model.replace("-latest", "")
            assert returned_model.startswith(base_model)
        else:
            assert model == returned_model

        # Verify usage structure
        usage = usage_data["usage"]
        assert "input_tokens" in usage
        assert "output_tokens" in usage
        assert isinstance(usage["input_tokens"], int)
        assert isinstance(usage["output_tokens"], int)
        assert usage["input_tokens"] > 0
        assert usage["output_tokens"] > 0


class TestAnthropicHandlerDetection:
    """Test that the Anthropic handler is properly detected."""

    def test_handler_detection_real_client(self):
        """Test that real Anthropic clients are detected correctly."""
        if not ANTHROPIC_AVAILABLE:
            pytest.skip("anthropic library not available")

        client = anthropic.Anthropic(api_key="test-key")
        proxy = LLMTrackingProxy(client, provider=Provider.ANTHROPIC)

        assert proxy.provider_name == "Anthropic"

    def test_anthropic_vs_openai_distinction(self):
        """Test that Anthropic clients are distinguished from OpenAI clients."""
        # Use MagicMock with a spec to create a strict mock
        mock_openai = MagicMock(
            spec=["chat", "completions", "_is_anthropic_mock"],
            __class__=MagicMock(__module__="openai.client"),
        )
        # Ensure the mock doesn't get misidentified
        delattr(mock_openai, "_is_anthropic_mock")

        proxy_openai = LLMTrackingProxy(mock_openai, provider=Provider.OPENAI)
        assert proxy_openai.provider_name == "OpenAI"

        # Use MagicMock with a spec for a strict Anthropic mock
        mock_anthropic = MagicMock(
            spec=["messages", "create", "_is_openai_mock"],
            __class__=MagicMock(__module__="anthropic.client"),
        )
        delattr(mock_anthropic, "_is_openai_mock")

        proxy_anthropic = LLMTrackingProxy(mock_anthropic, provider=Provider.ANTHROPIC)
        assert proxy_anthropic.provider_name == "Anthropic"


class TestAnthropicPayloadStructure:
    """Test that Anthropic usage payloads have the correct structure."""

    def test_payload_structure_with_mock(self):
        """Test payload structure using mock responses."""
        from llmcosts.tracker.anthropic_handler import AnthropicUsageHandler

        handler = AnthropicUsageHandler()

        # Mock response object with a spec to prevent new attributes
        mock_response = MagicMock(spec=["model", "usage", "service_tier"])
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        mock_response.usage.model_dump.return_value = {
            "input_tokens": 10,
            "output_tokens": 20,
        }
        # The handler checks for service_tier, so we mock it as not present.
        delattr(mock_response, "service_tier")

        payload = handler.extract_usage_payload(mock_response, attr=Mock())

        # Verify structure
        assert payload is not None
        assert "model_id" in payload
        assert "usage" in payload
        assert "response_id" in payload
        assert "timestamp" in payload
        assert payload["model_id"] == "claude-3-5-sonnet-20241022"
        assert payload["usage"]["input_tokens"] == 10
        assert payload["usage"]["output_tokens"] == 20

    def test_payload_structure_no_usage(self):
        """Test that None is returned when no usage data is available."""
        from llmcosts.tracker.anthropic_handler import AnthropicUsageHandler

        handler = AnthropicUsageHandler()

        # Mock response without usage, using a spec
        mock_response = MagicMock(spec=["model", "usage", "service_tier"])
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage = None
        # The handler checks for service_tier, so we mock it as not present.
        delattr(mock_response, "service_tier")

        payload = handler.extract_usage_payload(mock_response, attr=Mock())
        assert payload is None


class TestAnthropicValidation:
    """Test validation behavior for Anthropic streaming."""

    def test_streaming_validation_no_error(self):
        """Test that Anthropic streaming doesn't require special options."""
        from llmcosts.tracker.anthropic_handler import AnthropicUsageHandler

        handler = AnthropicUsageHandler()
        mock_client = Mock()
        mock_attr = Mock()  # Mock the callable attribute

        # Should not raise any errors
        handler.validate_streaming_options(mock_client, {"stream": True}, mock_attr)
        handler.validate_streaming_options(mock_client, {"stream": False}, mock_attr)
        handler.validate_streaming_options(mock_client, {}, mock_attr)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
