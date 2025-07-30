from pathlib import Path
from unittest.mock import patch

import boto3
import pytest
from environs import Env

from llmcosts.exceptions import TriggeredLimitError
from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider

env = Env()
env.read_env(Path(__file__).parent / ".env")


@pytest.fixture
def client():
    aws_access_key_id = env.str("AWS_ACCESS_KEY_ID", None)
    aws_secret_access_key = env.str("AWS_SECRET_ACCESS_KEY", None)
    region_name = env.str("AWS_DEFAULT_REGION", "us-east-1")
    if not aws_access_key_id or not aws_secret_access_key:
        pytest.skip("AWS credentials not configured")
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    )
    return session.client("bedrock-runtime", region_name=region_name)


@pytest.fixture
def tracked_client(client):
    return LLMTrackingProxy(client, provider=Provider.AMAZON_BEDROCK, debug=True)


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
        "provider": "amazon-bedrock",
        "model_id": "us.meta.llama3-3-70b-instruct-v1:0",
        "client_customer_key": None,
        "message": "Usage blocked: limit threshold of $1.00 exceeded",
    }
    return {
        "status": "checked",
        "allowed": False,
        "violations": [violation],
        "warnings": [],
    }


MODEL = "us.meta.llama3-3-70b-instruct-v1:0"


class TestBedrockLimit:
    def test_nonstreaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            res = tracked_client.converse(
                modelId=MODEL,
                messages=[{"role": "user", "content": [{"text": "Hello"}]}],
                inferenceConfig={"maxTokens": 10, "temperature": 0.1},
            )
            assert "output" in res

    def test_nonstreaming_blocked(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_block(),
        ):
            with pytest.raises(TriggeredLimitError):
                tracked_client.converse(
                    modelId=MODEL,
                    messages=[{"role": "user", "content": [{"text": "Hello"}]}],
                    inferenceConfig={"maxTokens": 10, "temperature": 0.1},
                )

    def test_streaming_allowed(self, tracked_client):
        with patch.object(
            tracked_client._llm_costs_client,
            "check_triggered_thresholds",
            return_value=_allow(),
        ):
            stream = tracked_client.converse_stream(
                modelId=MODEL,
                messages=[{"role": "user", "content": [{"text": "Count"}]}],
                inferenceConfig={"maxTokens": 10, "temperature": 0.1},
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
                    tracked_client.converse_stream(
                        modelId=MODEL,
                        messages=[{"role": "user", "content": [{"text": "hi"}]}],
                        inferenceConfig={"maxTokens": 10, "temperature": 0.1},
                    )
                )
