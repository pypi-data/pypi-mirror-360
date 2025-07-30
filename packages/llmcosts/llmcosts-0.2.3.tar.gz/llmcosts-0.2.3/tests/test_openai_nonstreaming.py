"""
Dedicated tests for OpenAI non-streaming usage tracking and cost event integration.

Focus: Non-streaming OpenAI API calls (chat completions, legacy completions, responses API).
"""

import json
import sys
from pathlib import Path

import openai
import pytest
from environs import Env

# Add the parent directory to sys.path so we can import from the main project
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

# Load environment variables from .env file in the tests directory
env = Env()
env.read_env(Path(__file__).parent / ".env")


class TestOpenAINonStreaming:
    """Test suite for LLMTrackingProxy with real OpenAI API non-streaming calls."""

    @pytest.fixture
    def openai_client(self):
        """Create a real OpenAI client."""
        api_key = env.str("OPENAI_API_KEY", None)
        if not api_key:
            pytest.skip(
                "OPENAI_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )

        # Use longer timeout to handle network latency issues
        return openai.OpenAI(api_key=api_key, timeout=30.0)

    @pytest.fixture
    def tracked_client(self, openai_client):
        """Create a tracked OpenAI client."""
        return LLMTrackingProxy(openai_client, provider=Provider.OPENAI, debug=True)

    # ========================================================================
    # CHAT COMPLETIONS API TESTS - NON-STREAMING
    # ========================================================================

    def test_chat_completions_non_streaming(self, tracked_client, caplog):
        """Test non-streaming chat completion captures usage with new payload format."""
        response = tracked_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": "Hi"}]
        )

        # Verify usage was printed with new format
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

        # Verify response is valid
        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0
        assert "gpt-4o-mini" in response.model

    # ========================================================================
    # LEGACY COMPLETIONS API TESTS - NON-STREAMING
    # ========================================================================

    def test_legacy_completions_non_streaming(self, tracked_client, caplog):
        """Test non-streaming legacy completion captures usage with new payload format."""
        response = tracked_client.completions.create(
            model="gpt-3.5-turbo-instruct",  # One of the few models that still supports legacy completions
            prompt="Say hello:",
            max_tokens=10,
        )
        assert response.choices[0].text
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-3.5-turbo-instruct" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

    # ========================================================================
    # RESPONSES API TESTS - NON-STREAMING
    # ========================================================================

    def test_responses_api_non_streaming(self, tracked_client, caplog):
        """Test non-streaming response creation (Azure OpenAI Responses API) with new payload format."""
        response = tracked_client.responses.create(
            model="gpt-4o-mini", input="Hi there!"
        )
        assert hasattr(response, "output_text") or hasattr(response, "output")
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text

    # ========================================================================
    # PAYLOAD STRUCTURE TESTS
    # ========================================================================

    def test_payload_structure_validation(self, tracked_client, caplog):
        """Test that usage data has the expected structure and new payload format."""
        response = tracked_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": "1+1=?"}]
        )
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text

        # The actual usage object should have proper structure
        usage = response.usage
        assert hasattr(usage, "completion_tokens")
        assert hasattr(usage, "prompt_tokens")
        assert hasattr(usage, "total_tokens")

        # Values should be positive integers
        assert isinstance(usage.completion_tokens, int)
        assert isinstance(usage.prompt_tokens, int)
        assert isinstance(usage.total_tokens, int)
        assert usage.completion_tokens > 0
        assert usage.prompt_tokens > 0
        assert usage.total_tokens > 0
        assert usage.total_tokens == usage.completion_tokens + usage.prompt_tokens

        # Check model field contains base model name
        assert "gpt-4o-mini" in response.model

        # service_tier may or may not be present
        if hasattr(response, "service_tier") and response.service_tier is not None:
            assert "service_tier" in caplog.text

    def test_payload_schema_completeness(self, tracked_client, caplog):
        """Test that the payload contains all required schema fields when available."""
        response = tracked_client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": "Hi"}]
        )

        # Capture the output and parse the JSON
        output_line = [
            line for line in caplog.text.split("\n") if "OpenAI usage →" in line
        ][0]
        usage_json_str = output_line.split("OpenAI usage → ")[1]
        payload = json.loads(usage_json_str)

        # Verify required fields are present in the parsed payload
        assert "usage" in payload, "Payload should contain 'usage' field"
        assert "model_id" in payload, "Payload should contain 'model_id' field"
        assert "response_id" in payload, "Payload should contain 'response_id' field"
        assert "timestamp" in payload, "Payload should contain 'timestamp' field"
        assert "gpt-4o-mini" in payload["model_id"]

        # Check if service_tier is available and included if present
        if hasattr(response, "service_tier") and response.service_tier is not None:
            assert "service_tier" in payload, (
                "Payload should contain 'service_tier' field when available"
            )

    # ========================================================================
    # CROSS-PROVIDER TESTS
    # ========================================================================

    def test_non_openai_client_bypasses_validation(self):
        """Test that non-OpenAI clients bypass the stream_options validation."""
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.__class__.__module__ = "anthropic.client"
        mock_client.__class__.__name__ = "Anthropic"
        mock_client._is_openai_mock = False

        tracked_client = LLMTrackingProxy(mock_client, provider=Provider.ANTHROPIC)

        # Setup mock to return a simple response object
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_create = Mock(return_value=mock_response)
        tracked_client._target.messages = Mock()
        tracked_client._target.messages.create = mock_create

        # This should work fine for non-OpenAI client (non-streaming)
        response = tracked_client.messages.create(
            model="claude-3",
            messages=[{"role": "user", "content": "Hello"}],
        )
        assert response == mock_response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
