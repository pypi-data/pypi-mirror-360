"""
Dedicated tests for Gemini streaming usage tracking and cost event integration.

Focus: Streaming Gemini API calls (generate_content_stream).
"""

import os

import pytest
from environs import Env

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

try:
    import google.genai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Skip all tests if the library isn't installed
pytestmark = pytest.mark.skipif(
    not GEMINI_AVAILABLE, reason="google-genai library not installed"
)

# Load env
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))

GEMINI_MODELS = [
    "gemini-2.5-flash",
    # "gemini-2.5-pro",
    "gemini-2.5-flash-lite-preview-06-17",
]


class TestGeminiStreaming:
    """Test suite for LLMTrackingProxy with real Gemini API streaming calls."""

    @pytest.fixture
    def gemini_client(self):
        """Create a tracked Gemini client."""
        api_key = env.str("GOOGLE_API_KEY", None)
        if not api_key:
            pytest.skip(
                "GOOGLE_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )
        client = genai.Client(api_key=api_key)
        return LLMTrackingProxy(client, provider=Provider.GOOGLE, debug=True)

    @pytest.mark.parametrize("model", GEMINI_MODELS)
    def test_generate_content_streaming(self, gemini_client, model, caplog):
        """Test streaming content generation captures usage with correct format."""
        stream = gemini_client.models.generate_content_stream(
            model=model, contents="Hello streaming"
        )
        chunks = list(stream)
        assert len(chunks) > 0

        # Verify usage tracking
        assert "[LLM costs] Gemini usage →" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text

    def test_gemini_streaming_detailed(self, gemini_client, caplog):
        """Test streaming Gemini call with detailed validation."""
        stream = gemini_client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents="Count from 1 to 5, one number per line.",
        )

        # Consume the stream and verify we get chunks
        chunks = []
        for chunk in stream:
            chunks.append(chunk)

        assert len(chunks) > 0, "Should have received streaming chunks"

        # Verify usage tracking
        assert "[LLM costs] Gemini usage →" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
