"""
Dedicated tests for Gemini non-streaming usage tracking and cost event integration.

Focus: Non-streaming Gemini API calls (generate_content).
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


class TestGeminiNonStreaming:
    """Test suite for LLMTrackingProxy with real Gemini API non-streaming calls."""

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
    def test_generate_content(self, gemini_client, model, caplog):
        """Test non-streaming content generation captures usage with correct format."""
        response = gemini_client.models.generate_content(
            model=model, contents="Hello from Gemini"
        )
        assert "[LLM costs] Gemini usage →" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert response.text

    def test_gemini_non_streaming_detailed(self, gemini_client, caplog):
        """Test non-streaming Gemini call with detailed validation."""
        response = gemini_client.models.generate_content(
            model="gemini-1.5-flash",
            contents="What is the capital of France? Answer in one word.",
        )

        # Verify response is valid
        assert response.text is not None
        assert len(response.text.strip()) > 0

        # Verify usage tracking
        assert "[LLM costs] Gemini usage →" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
