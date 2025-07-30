"""
Tests for OpenAI Responses API limit checking.

Note: These tests require network connectivity to OpenAI API and may be flaky
due to network timeouts or OpenAI API availability. Tests include retry logic
and will skip if persistent network issues occur.
"""

from pathlib import Path
from unittest.mock import patch

import openai
import pytest
from environs import Env

from llmcosts.exceptions import TriggeredLimitError
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

# Load env vars
env = Env()
env.read_env(Path(__file__).parent / ".env")


@pytest.fixture
def openai_client():
    api_key = env.str("OPENAI_API_KEY", None)
    if not api_key:
        pytest.skip(
            "OPENAI_API_KEY not found in environment variables or tests/.env file"
        )
    # Use longer timeout to handle network latency issues
    return openai.OpenAI(api_key=api_key, timeout=30.0)


@pytest.fixture
def tracked_client(openai_client):
    return LLMTrackingProxy(openai_client, provider=Provider.OPENAI, debug=True)


def _allow():
    return {"status": "checked", "allowed": True, "violations": [], "warnings": []}


def _block():
    violation = {
        "event_id": "ca23a271-7419-48ab-871f-b9eb36a2c73d",
        "threshold_type": "limit",
        "amount": "1.00",
        "period": "daily",
        "triggered_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-01-02T00:00:00Z",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "client_customer_key": None,
        "message": "Usage blocked: limit threshold of $1.00 exceeded",
    }
    return {
        "status": "checked",
        "allowed": False,
        "violations": [violation],
        "warnings": [],
    }


@pytest.mark.network
class TestOpenAIResponsesLimit:
    def test_responses_nonstreaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            # Retry logic for network timeouts
            max_retries = 3
            last_exception = None

            for attempt in range(max_retries):
                try:
                    res = tracked_client.responses.create(
                        model="gpt-4o-mini", input="hi"
                    )
                    assert res
                    return  # Success, exit the test
                except (openai.APITimeoutError, openai.APIConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        print(f"Network timeout on attempt {attempt + 1}, retrying...")
                        continue
                    else:
                        pytest.skip(
                            f"Skipping test due to persistent network issues: {e}"
                        )
                except Exception as e:
                    # Re-raise non-network exceptions immediately
                    raise e

    def test_responses_nonstreaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                tracked_client.responses.create(
                    model="gpt-4o-mini",
                    input="hi",
                )

    def test_responses_streaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            stream = tracked_client.responses.create(
                model="gpt-4o-mini",
                input="count to 3",
                stream=True,
            )
            chunks = list(stream)
            assert len(chunks) > 0

    def test_responses_streaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                list(
                    tracked_client.responses.create(
                        model="gpt-4o-mini",
                        input="hi",
                        stream=True,
                    )
                )
