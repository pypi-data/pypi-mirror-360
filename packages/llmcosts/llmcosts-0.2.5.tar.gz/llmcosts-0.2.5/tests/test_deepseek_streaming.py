"""
Dedicated tests for DeepSeek streaming usage tracking and cost event integration.

Focus: Streaming DeepSeek API calls using OpenAI-compatible client.
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


class TestDeepSeekStreaming:
    """Test suite for LLMTrackingProxy with DeepSeek API streaming calls using OpenAI-compatible client."""

    @pytest.fixture
    def deepseek_client(self):
        """Create a DeepSeek client using OpenAI-compatible interface."""
        api_key = env.str("DEEPSEEK_API_KEY", None)
        if not api_key:
            pytest.skip(
                "DEEPSEEK_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )

        return openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")

    @pytest.fixture
    def tracked_deepseek_client(self, deepseek_client):
        """Create a tracked DeepSeek client with auto-extracted base_url."""
        return LLMTrackingProxy(
            deepseek_client,
            provider=Provider.OPENAI,
            debug=True,
        )

    def test_base_url_extraction(self, deepseek_client, tracked_deepseek_client):
        """Test that base_url is automatically extracted from the OpenAI client."""
        # Verify the original client has the correct base_url
        assert deepseek_client.base_url == "https://api.deepseek.com/v1/"

        # Verify the tracked client auto-extracted the base_url
        assert tracked_deepseek_client.base_url == "https://api.deepseek.com/v1/"

        # Verify the internal _base_url is set correctly
        assert tracked_deepseek_client._base_url == "https://api.deepseek.com/v1/"

    def test_deepseek_chat_completions_streaming(self, tracked_deepseek_client, caplog):
        """Test streaming chat completion with DeepSeek captures usage."""
        stream = tracked_deepseek_client.chat.completions.create(
            model="deepseek-chat",
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

        # Verify usage tracking
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "deepseek" in caplog.text.lower()
        assert "completion_tokens" in caplog.text
        assert "prompt_tokens" in caplog.text
        assert "total_tokens" in caplog.text

        # Verify base_url is included in the usage payload
        assert "https://api.deepseek.com/v1/" in caplog.text

        # Verify streaming structure
        content_chunks = [c for c in chunks if c.choices and c.choices[0].delta.content]
        usage_chunks = [c for c in chunks if c.usage is not None]
        assert len(content_chunks) > 0, "Should have content chunks"
        assert len(usage_chunks) == 1, "Should have exactly one usage chunk"

    def test_deepseek_streaming_code_generation(self, tracked_deepseek_client, caplog):
        """Test streaming DeepSeek for code generation task."""
        stream = tracked_deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": "Write a simple function to multiply two numbers. Keep it short.",
                }
            ],
            stream=True,
            stream_options={"include_usage": True},
        )

        # Consume the stream and collect chunks
        chunks = []
        for chunk in stream:
            chunks.append(chunk)

        # Verify we got streaming chunks
        assert len(chunks) > 0

        # Verify usage tracking
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "deepseek" in caplog.text.lower()

        # Verify base_url is included in the usage payload
        assert "https://api.deepseek.com/v1/" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
