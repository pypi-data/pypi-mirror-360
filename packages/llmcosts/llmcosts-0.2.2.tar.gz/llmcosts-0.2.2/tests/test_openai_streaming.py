"""
Dedicated tests for OpenAI streaming usage tracking and cost event integration.

Focus: Streaming OpenAI API calls (chat completions, legacy completions, responses API) and validation.
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


class TestOpenAIStreaming:
    """Test suite for LLMTrackingProxy with real OpenAI API streaming calls."""

    @pytest.fixture
    def openai_client(self):
        """Create a real OpenAI client."""
        api_key = env.str("OPENAI_API_KEY", None)
        if not api_key:
            pytest.skip(
                "OPENAI_API_KEY not found in environment variables or tests/.env file. "
                "Please copy env.example to tests/.env and add your API keys."
            )

        return openai.OpenAI(api_key=api_key)

    @pytest.fixture
    def tracked_client(self, openai_client):
        """Create a tracked OpenAI client."""
        return LLMTrackingProxy(openai_client, provider=Provider.OPENAI, debug=True)

    # ========================================================================
    # CHAT COMPLETIONS API TESTS - STREAMING
    # ========================================================================

    def test_chat_completions_streaming_with_usage_options(
        self, tracked_client, caplog
    ):
        """Test streaming chat completion with correct stream_options works and captures usage."""
        stream = tracked_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hi"}],
            stream=True,
            stream_options={"include_usage": True},
        )

        # Consume the stream
        chunks = list(stream)
        assert len(chunks) > 0

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

        # Verify streaming structure
        content_chunks = [c for c in chunks if c.choices and c.choices[0].delta.content]
        usage_chunks = [c for c in chunks if c.usage is not None]
        assert len(content_chunks) > 0, "Should have content chunks"
        assert len(usage_chunks) == 1, "Should have exactly one usage chunk"

    # ========================================================================
    # LEGACY COMPLETIONS API TESTS - STREAMING
    # ========================================================================

    def test_legacy_completions_streaming_with_usage_options(
        self, tracked_client, caplog
    ):
        """Test streaming legacy completion with correct stream_options works and captures usage."""
        stream = tracked_client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt="Count: 1, 2,",
            max_tokens=10,
            stream=True,
            stream_options={"include_usage": True},
        )
        for chunk in stream:
            pass
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
    # RESPONSES API TESTS - STREAMING
    # ========================================================================

    def test_responses_api_streaming(self, tracked_client, caplog):
        """Test streaming response creation (Azure OpenAI Responses API)."""
        stream = tracked_client.responses.create(
            model="gpt-4o-mini",
            input="Count to 3",
            stream=True,
        )
        for chunk in stream:
            pass
        assert "[LLM costs] OpenAI usage →" in caplog.text
        assert "usage" in caplog.text
        assert "model" in caplog.text
        assert "response_id" in caplog.text
        assert "timestamp" in caplog.text
        assert "gpt-4o-mini" in caplog.text

    # ========================================================================
    # VALIDATION TESTS
    # ========================================================================

    def test_chat_completions_streaming_validation_missing_options(
        self, tracked_client
    ):
        """Test that chat completions streaming without stream_options raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            tracked_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                stream=True,  # Missing stream_options!
            )

        assert "stream_options={'include_usage': True}" in str(exc_info.value)
        assert "OpenAI streaming calls require" in str(exc_info.value)

    def test_chat_completions_streaming_validation_wrong_options(self, tracked_client):
        """Test that chat completions streaming with wrong stream_options raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            tracked_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                stream=True,
                stream_options={"include_usage": False},  # Wrong value!
            )

        assert "stream_options={'include_usage': True}" in str(exc_info.value)

    def test_legacy_completions_streaming_validation(self, tracked_client):
        """Test that legacy completions streaming also requires stream_options."""
        with pytest.raises(ValueError) as exc_info:
            tracked_client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt="Hi",
                stream=True,  # Missing stream_options!
            )

        assert "stream_options={'include_usage': True}" in str(exc_info.value)

    def test_responses_api_streaming_no_validation_required(self, tracked_client):
        """Test that Responses API streaming does NOT require stream_options validation."""
        # This should NOT raise an exception - Responses API doesn't need stream_options
        try:
            stream = tracked_client.responses.create(
                model="gpt-4o-mini",
                input="Hello",
                stream=True,  # No stream_options needed for Responses API
            )
            # Consume just the first chunk to verify it works
            next(iter(stream))
        except ValueError as e:
            if "stream_options" in str(e):
                pytest.fail(
                    "Responses API streaming should not require stream_options validation, "
                    f"but got error: {e}"
                )
        except Exception:
            # Other exceptions (like network errors) are fine, we just want to ensure
            # the validation doesn't trigger
            pass

    def test_chat_completions_vs_responses_validation_distinction(self, tracked_client):
        """Test that validation correctly distinguishes between chat completions and responses APIs."""

        # Chat completions should require stream_options
        with pytest.raises(ValueError) as exc_info:
            tracked_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hi"}],
                stream=True,  # Missing stream_options!
            )
        assert "stream_options={'include_usage': True}" in str(exc_info.value)

        # Responses API should NOT require stream_options (should not raise ValueError about stream_options)
        try:
            stream = tracked_client.responses.create(
                model="gpt-4o-mini",
                input="Hello",
                stream=True,  # No stream_options needed
            )
            # Consume just the first chunk to verify validation doesn't block it
            next(iter(stream))
        except ValueError as e:
            if "stream_options" in str(e):
                pytest.fail(
                    f"Responses API should not require stream_options, but got: {e}"
                )
        except Exception:
            # Other exceptions are fine, we just care about validation
            pass

    def test_non_openai_client_bypasses_streaming_validation(self):
        """Test that non-OpenAI clients bypass the stream_options validation for streaming."""
        from unittest.mock import Mock

        mock_client = Mock()
        mock_client.__class__.__module__ = "anthropic.client"
        mock_client.__class__.__name__ = "Anthropic"
        mock_client._is_openai_mock = False

        tracked_client = LLMTrackingProxy(mock_client, provider=Provider.ANTHROPIC)

        # Setup mock to return empty iterator
        mock_create = Mock(return_value=iter([]))
        tracked_client._target.messages = Mock()
        tracked_client._target.messages.create = mock_create

        # This should NOT raise an exception (non-OpenAI client)
        try:
            stream = tracked_client.messages.create(
                model="claude-3",
                messages=[{"role": "user", "content": "Hello"}],
                stream=True,  # No stream_options, but should be fine for non-OpenAI
            )
            list(stream)  # Consume the stream
        except ValueError as e:
            if "stream_options" in str(e):
                pytest.fail(
                    "Non-OpenAI client should not require stream_options validation"
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
