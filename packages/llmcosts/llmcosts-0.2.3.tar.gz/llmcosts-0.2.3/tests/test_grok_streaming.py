"""
Dedicated tests for Grok streaming usage tracking and cost event integration.

Focus: Streaming Grok API calls using OpenAI-compatible client.
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


class TestGrokStreaming:
    """Test suite for LLMTrackingProxy with Grok API streaming calls using OpenAI-compatible client."""

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

    def test_grok_streaming_basic(self, tracked_grok_client, caplog):
        """Test basic Grok streaming functionality."""
        try:
            stream = tracked_grok_client.chat.completions.create(
                model="grok-3-mini",
                messages=[{"role": "user", "content": "Count from 1 to 3"}],
                stream=True,
                stream_options={"include_usage": True},
            )

            # Consume the stream and collect chunks
            chunks = []
            for chunk in stream:
                chunks.append(chunk)

            # Verify we got streaming chunks
            assert len(chunks) > 0

        except openai.NotFoundError as e:
            pytest.skip(f"Grok streaming not accessible: {e}")

        # Verify usage tracking
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

        # Verify streaming structure
        content_chunks = [c for c in chunks if c.choices and c.choices[0].delta.content]
        usage_chunks = [c for c in chunks if c.usage is not None]
        assert len(content_chunks) > 0, "Should have content chunks"
        assert len(usage_chunks) == 1, "Should have exactly one usage chunk"

    def test_grok_streaming_conversation(self, tracked_grok_client, caplog):
        """Test Grok streaming with conversational input."""
        try:
            stream = tracked_grok_client.chat.completions.create(
                model="grok-3-mini",
                messages=[
                    {"role": "user", "content": "What is AI? Give a short answer."}
                ],
                max_tokens=50,
                stream=True,
                stream_options={"include_usage": True},
            )

            # Consume the stream and collect chunks
            chunks = []
            for chunk in stream:
                chunks.append(chunk)

            # Verify we got streaming chunks
            assert len(chunks) > 0

        except openai.NotFoundError as e:
            pytest.skip(f"Grok streaming not accessible: {e}")

        # Verify usage tracking
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text

    def test_grok_streaming_validation(self, tracked_grok_client):
        """Test that Grok streaming requires stream_options for usage tracking."""
        # Since Grok uses OpenAI-compatible client, it should require stream_options
        with pytest.raises(ValueError) as exc_info:
            tracked_grok_client.chat.completions.create(
                model="grok-3-mini",
                messages=[{"role": "user", "content": "Hello"}],
                stream=True,  # Missing stream_options!
            )

        assert "stream_options={'include_usage': True}" in str(exc_info.value)
        assert "OpenAI streaming calls require" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
