"""
Dedicated tests for Grok non-streaming usage tracking and cost event integration.

Focus: Non-streaming Grok API calls using OpenAI-compatible client.
"""

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


class TestGrokNonStreaming:
    """Test suite for LLMTrackingProxy with Grok API non-streaming calls using OpenAI-compatible client."""

    @pytest.fixture
    def grok_client(self):
        """Create a Grok client using OpenAI-compatible interface."""
        api_key = env.str("GROK_API_KEY", None)
        if not api_key:
            pytest.skip(
                "GROK_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )

        return openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    @pytest.fixture
    def tracked_grok_client(self, grok_client):
        """Create a tracked Grok client."""
        return LLMTrackingProxy(
            grok_client,
            provider=Provider.OPENAI,
            base_url="https://api.x.ai/v1",
            debug=True,
        )

    def test_grok_3_mini_model(self, tracked_grok_client, caplog):
        """Test Grok 3 mini model captures usage correctly."""
        try:
            response = tracked_grok_client.chat.completions.create(
                model="grok-3-mini",
                messages=[{"role": "user", "content": "Hello, how are you?"}],
                max_tokens=100,  # Enough tokens for reasoning + visible output
            )
        except openai.NotFoundError as e:
            pytest.skip(f"Grok 3 mini model not accessible: {e}")

        # Grok-3-mini is a reasoning model - check both content and reasoning_content
        message = response.choices[0].message
        has_content = bool(message.content and message.content.strip())
        has_reasoning = bool(getattr(message, "reasoning_content", None))
        assert has_content or has_reasoning, (
            "Should have either content or reasoning_content"
        )

        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

    def test_grok_conversation(self, tracked_grok_client, caplog):
        """Test Grok conversational capabilities."""
        try:
            response = tracked_grok_client.chat.completions.create(
                model="grok-3-mini",
                messages=[
                    {"role": "user", "content": "What is 2+2?"},
                ],
                max_tokens=100,  # Increased to allow reasoning + visible output
            )
        except openai.NotFoundError as e:
            pytest.skip(f"Grok model not accessible: {e}")

        # Grok-3-mini is a reasoning model - check both content and reasoning_content
        message = response.choices[0].message
        has_content = bool(message.content and message.content.strip())
        has_reasoning = bool(getattr(message, "reasoning_content", None))
        assert has_content or has_reasoning, (
            "Should have either content or reasoning_content"
        )

        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text

    def test_grok_payload_structure(self, tracked_grok_client, caplog):
        """Test that Grok usage payloads have the expected structure."""
        try:
            response = tracked_grok_client.chat.completions.create(
                model="grok-3-mini",
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=50,  # Increased to allow for proper response
            )
        except openai.NotFoundError as e:
            pytest.skip(f"Grok model not accessible: {e}")

        # Verify the response structure
        assert hasattr(response, "usage")
        assert hasattr(response.usage, "completion_tokens")
        assert hasattr(response.usage, "prompt_tokens")
        assert hasattr(response.usage, "total_tokens")

        # Verify token counts are reasonable
        # Note: Grok-3-mini is a reasoning model that may have 0 completion_tokens but positive reasoning_tokens
        usage_details = getattr(response.usage, "completion_tokens_details", None)
        reasoning_tokens = (
            getattr(usage_details, "reasoning_tokens", 0) if usage_details else 0
        )

        # Either completion_tokens > 0 OR reasoning_tokens > 0 (for reasoning models)
        total_output_tokens = response.usage.completion_tokens + reasoning_tokens
        assert total_output_tokens > 0, (
            f"Should have some output tokens (completion: {response.usage.completion_tokens}, reasoning: {reasoning_tokens})"
        )
        assert response.usage.prompt_tokens > 0
        assert response.usage.total_tokens > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
