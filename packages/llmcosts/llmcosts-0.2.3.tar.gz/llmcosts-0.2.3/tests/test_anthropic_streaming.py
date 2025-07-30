"""
Dedicated tests for Anthropic streaming usage tracking and cost event integration.

Focus: Streaming Anthropic Claude API calls (messages.create with stream=True).
"""

import json
import os

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


class TestAnthropicStreaming:
    """Test streaming Anthropic Claude API calls."""

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
    def test_messages_create_streaming(self, anthropic_client, model, caplog):
        """Test streaming messages.create with various Claude models."""
        stream = anthropic_client.messages.create(
            model=model,
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Count from 1 to 5, one number per line."}
            ],
            stream=True,
        )

        # Collect all chunks
        chunks = []
        for chunk in stream:
            chunks.append(chunk)

        # Verify we got chunks
        assert len(chunks) > 0

        # Check that usage information was captured and printed
        assert "[LLM costs] Anthropic usage →" in caplog.text

        # Parse the printed JSON to verify structure
        usage_lines = [
            line for line in caplog.text.split("\n") if "Anthropic usage →" in line
        ]
        assert len(usage_lines) > 0

        # Check the final usage data (should be in the last chunk)
        final_usage_line = usage_lines[-1]
        usage_json_str = final_usage_line.split("Anthropic usage → ")[1]
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
