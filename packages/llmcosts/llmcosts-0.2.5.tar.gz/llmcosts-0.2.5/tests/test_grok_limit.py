import sys
from pathlib import Path
from unittest.mock import patch

import openai
import pytest
from environs import Env

from llmcosts.exceptions import TriggeredLimitError
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

# Add the parent directory to sys.path so we can import from the main project
sys.path.insert(0, str(Path(__file__).parent.parent))


env = Env()
env.read_env(Path(__file__).parent / ".env")


@pytest.fixture
def client():
    api_key = env.str("GROK_API_KEY", None)
    if not api_key:
        pytest.skip(
            "GROK_API_KEY not found in environment variables or tests/.env file. "
            "Please copy env.example to tests/.env and add your API keys."
        )
    return openai.OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )


@pytest.fixture
def tracked_client(client):
    return LLMTrackingProxy(
        client,
        provider=Provider.OPENAI,
        base_url="https://api.x.ai/v1",
        debug=True,
    )


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
        "provider": "xai",
        "model_id": "grok-3-mini",
        "client_customer_key": None,
        "message": "Usage blocked: limit threshold of $1.00 exceeded",
    }
    return {
        "status": "checked",
        "allowed": False,
        "violations": [violation],
        "warnings": [],
    }


class TestGrokLimit:
    def test_nonstreaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            res = tracked_client.chat.completions.create(
                model="grok-3-mini",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            assert res.choices

    def test_nonstreaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                tracked_client.chat.completions.create(
                    model="grok-3-mini",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "hi"}],
                )

    def test_streaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            stream = tracked_client.chat.completions.create(
                model="grok-3-mini",
                max_tokens=10,
                messages=[{"role": "user", "content": "count"}],
                stream=True,
                stream_options={"include_usage": True},
            )
            chunks = list(stream)
            assert len(chunks) > 0

    def test_streaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                list(
                    tracked_client.chat.completions.create(
                        model="grok-3-mini",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "hi"}],
                        stream=True,
                        stream_options={"include_usage": True},
                    )
                )
