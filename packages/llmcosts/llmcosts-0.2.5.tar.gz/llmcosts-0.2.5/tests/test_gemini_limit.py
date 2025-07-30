from pathlib import Path
from unittest.mock import patch

import pytest
from environs import Env

from llmcosts.exceptions import TriggeredLimitError
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

try:
    import google.genai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not GEMINI_AVAILABLE, reason="google-genai library not installed"
)

env = Env()
env.read_env(Path(__file__).parent / ".env")


@pytest.fixture
def client():
    api_key = env.str("GOOGLE_API_KEY", None)
    if not api_key:
        pytest.skip("GOOGLE_API_KEY not configured")
    return genai.Client(api_key=api_key)


@pytest.fixture
def tracked_client(client):
    return LLMTrackingProxy(client, provider=Provider.GOOGLE, debug=True)


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
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "client_customer_key": None,
        "message": "Usage blocked: limit threshold of $1.00 exceeded",
    }
    return {
        "status": "checked",
        "allowed": False,
        "violations": [violation],
        "warnings": [],
    }


MODEL = "gemini-2.5-flash"


class TestGeminiLimit:
    def test_nonstreaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            res = tracked_client.models.generate_content(model=MODEL, contents="hi")
            assert res.text

    def test_nonstreaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                tracked_client.models.generate_content(model=MODEL, contents="hi")

    def test_streaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            stream = tracked_client.models.generate_content_stream(
                model=MODEL,
                contents="count",
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
                    tracked_client.models.generate_content_stream(
                        model=MODEL,
                        contents="hi",
                    )
                )
