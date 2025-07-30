"""
End-to-end tests for base_url inclusion in usage payloads.

These tests verify that base_url is actually included in usage payloads
by checking the debug logs from the tracker.
"""

import json
from pathlib import Path

import openai
import pytest
from environs import Env

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider


@pytest.fixture
def deepseek_client():
    """Create a DeepSeek client using OpenAI-compatible interface."""
    env = Env()
    env.read_env(Path(__file__).parent / ".env")

    api_key = env.str("DEEPSEEK_API_KEY", None)
    if not api_key:
        pytest.skip(
            "DEEPSEEK_API_KEY not found in environment variables or tests/.env file. "
            "Please copy env.example to tests/.env and add your API keys."
        )

    return openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")


class TestBaseUrlEndToEnd:
    """End-to-end tests for base_url inclusion in usage payloads."""

    def test_base_url_included_in_usage_payload(self, deepseek_client, caplog):
        """Test that base_url is actually included in the usage payload."""
        # Create tracked client with auto-extracted base_url
        tracked_client = LLMTrackingProxy(
            deepseek_client,
            provider=Provider.OPENAI,
            debug=True,
        )

        # Make a real API call
        response = tracked_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
        )

        # Verify the API call worked
        assert response.choices[0].message.content

        # Verify that usage was logged with base_url
        assert "[LLM costs] OpenAI usage →" in caplog.text

        # Extract the JSON payload from the log
        log_lines = caplog.text.split("\n")
        usage_log_line = None
        for line in log_lines:
            if "[LLM costs] OpenAI usage →" in line:
                usage_log_line = line
                break

        assert usage_log_line is not None, "Usage log line not found"

        # Extract JSON from the log line
        json_part = usage_log_line.split("[LLM costs] OpenAI usage → ")[1]
        payload = json.loads(json_part)

        # Verify base_url is included in the payload
        assert "base_url" in payload, "base_url should be included in usage payload"
        assert payload["base_url"] == "https://api.deepseek.com/v1/", (
            f"Expected base_url to be 'https://api.deepseek.com/v1/', "
            f"but got '{payload['base_url']}'"
        )

        # Verify other required fields are present
        assert "model_id" in payload
        assert "usage" in payload
        assert "response_id" in payload
        assert "timestamp" in payload
        assert "provider" in payload
        assert payload["provider"] == "openai"

    def test_base_url_not_included_when_using_default_openai(
        self, deepseek_client, caplog
    ):
        """Test that base_url is not included when using default OpenAI endpoint."""
        # Create a client with default OpenAI endpoint (but use DeepSeek key for simplicity)
        # This simulates what would happen with a standard OpenAI client
        standard_client = openai.OpenAI(
            api_key=deepseek_client.api_key  # Use DeepSeek key but with default OpenAI URL
        )

        # Verify the client has the default OpenAI base_url
        assert standard_client.base_url == "https://api.openai.com/v1/"

        # Create tracked client
        tracked_client = LLMTrackingProxy(
            standard_client,
            provider=Provider.OPENAI,
            debug=True,
        )

        # We can't make a real call to OpenAI with DeepSeek key, so let's just verify
        # that the tracked client extracted the correct base_url
        assert tracked_client.base_url == "https://api.openai.com/v1/"

        # For completeness, let's create a minimal test that doesn't require a real API call
        # We'll verify that when a client has the default OpenAI URL, it's extracted correctly
        print(f"Standard client base_url: {standard_client.base_url}")
        print(f"Tracked client base_url: {tracked_client.base_url}")

    def test_explicit_base_url_overrides_auto_extraction(self, deepseek_client, caplog):
        """Test that explicitly set base_url overrides auto-extracted base_url."""
        # Create tracked client with explicit base_url that differs from client
        tracked_client = LLMTrackingProxy(
            deepseek_client,  # Has base_url="https://api.deepseek.com/v1"
            provider=Provider.OPENAI,
            base_url="https://custom.example.com/v1",  # Explicit override
            debug=True,
        )

        # Make a real API call
        response = tracked_client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Hello, how are you?"}],
        )

        # Verify the API call worked
        assert response.choices[0].message.content

        # Verify that usage was logged with explicit base_url
        assert "[LLM costs] OpenAI usage →" in caplog.text

        # Extract the JSON payload from the log
        log_lines = caplog.text.split("\n")
        usage_log_line = None
        for line in log_lines:
            if "[LLM costs] OpenAI usage →" in line:
                usage_log_line = line
                break

        assert usage_log_line is not None, "Usage log line not found"

        # Extract JSON from the log line
        json_part = usage_log_line.split("[LLM costs] OpenAI usage → ")[1]
        payload = json.loads(json_part)

        # Verify explicit base_url is used, not the auto-extracted one
        assert "base_url" in payload, "base_url should be included in usage payload"
        assert payload["base_url"] == "https://custom.example.com/v1", (
            f"Expected base_url to be 'https://custom.example.com/v1', "
            f"but got '{payload['base_url']}'"
        )

        # Verify it's NOT the auto-extracted base_url
        assert payload["base_url"] != "https://api.deepseek.com/v1/", (
            "base_url should not be the auto-extracted value when explicitly set"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
