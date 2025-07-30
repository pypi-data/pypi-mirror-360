from pathlib import Path
from unittest.mock import patch

import pytest
from environs import Env

from llmcosts.exceptions import TriggeredLimitError
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

try:
    import anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not ANTHROPIC_AVAILABLE, reason="anthropic library not installed"
)

env = Env()
env.read_env(Path(__file__).parent / ".env")


@pytest.fixture
def client():
    api_key = env.str("ANTHROPIC_API_KEY", None)
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not configured")
    return anthropic.Anthropic(api_key=api_key)


@pytest.fixture
def tracked_client(client):
    return LLMTrackingProxy(client, provider=Provider.ANTHROPIC, debug=True)


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
        "provider": "anthropic",
        "model_id": "claude-3-5-haiku-20241022",
        "client_customer_key": None,
        "message": "Usage blocked: limit threshold of $1.00 exceeded",
    }
    return {
        "status": "checked",
        "allowed": False,
        "violations": [violation],
        "warnings": [],
    }


class TestAnthropicLimit:
    def test_nonstreaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            res = tracked_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "hi"}],
            )
            assert res.content or res.content[0]

    def test_nonstreaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                tracked_client.messages.create(
                    model="claude-3-5-haiku-20241022",
                    max_tokens=10,
                    messages=[{"role": "user", "content": "hi"}],
                )

    def test_streaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            stream = tracked_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "count"}],
                stream=True,
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
                    tracked_client.messages.create(
                        model="claude-3-5-haiku-20241022",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "hi"}],
                        stream=True,
                    )
                )
