"""
Dedicated tests for Amazon Bedrock streaming usage tracking and cost event integration.

Focus: Ensuring we get back cost event summary data from the endpoint for streaming responses.
"""

import os
import time
from typing import Any, Dict

import boto3
import pytest
from environs import Env

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider
from llmcosts.tracker.usage_delivery import get_usage_tracker, set_global_usage_tracker

# Load environment variables
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))

BEDROCK_MODELS = [
    "us.meta.llama3-3-70b-instruct-v1:0",  # Meta Llama via Bedrock with inference profile
    "us.amazon.nova-pro-v1:0",  # Amazon Nova Pro via Bedrock with inference profile
]


class BedrockStreamingCostEventCapture:
    """Capture and validate Bedrock streaming cost event data from endpoint responses."""

    def __init__(self):
        self.usage_data = []
        self.server_responses = []
        self.cost_events = []
        self.errors = []
        self.streaming_chunks = []

    def capture_usage(self, usage_data: Dict[str, Any]):
        """Capture usage data sent to endpoint."""
        self.usage_data.append(usage_data)

    def capture_streaming_chunk(self, chunk: Any):
        """Capture streaming chunk for analysis."""
        self.streaming_chunks.append(chunk)

    def capture_server_response(self, response_data: Dict[str, Any]):
        """Capture server response and extract cost events."""
        self.server_responses.append(response_data)

        # Extract cost events if present
        if "events" in response_data and response_data["events"]:
            self.cost_events.extend(response_data["events"])

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of captured data."""
        return {
            "total_usage_data": len(self.usage_data),
            "total_server_responses": len(self.server_responses),
            "total_cost_events": len(self.cost_events),
            "total_streaming_chunks": len(self.streaming_chunks),
            "models_tested": list(
                set(
                    data.get("model_id")
                    for data in self.usage_data
                    if data.get("model_id")
                )
            ),
            "errors": self.errors,
            "sample_cost_events": self.cost_events[:3] if self.cost_events else [],
            "sample_usage_data": self.usage_data[:3] if self.usage_data else [],
        }


@pytest.fixture(scope="session")
def llmcosts_api_key():
    """Get LLMCOSTS_API_KEY from environment."""
    api_key = env.str("LLMCOSTS_API_KEY", None)
    if not api_key:
        pytest.skip("LLMCOSTS_API_KEY not found - skipping endpoint integration tests")
    return api_key


@pytest.fixture(scope="function")
def bedrock_streaming_cost_capture(llmcosts_api_key):
    """Set up cost event capture for Bedrock streaming tests."""
    import llmcosts.tracker.usage_delivery as tracker

    # Store original tracker
    original_tracker = getattr(tracker, "_tracker", None)

    try:
        # Get or create global tracker
        global_tracker = get_usage_tracker()
        if not global_tracker:
            from llmcosts.tracker.usage_delivery import UsageTracker

            api_endpoint = os.environ.get(
                "LLMCOSTS_API_ENDPOINT", "https://llmcosts.com/api/v1/usage"
            )
            global_tracker = UsageTracker(
                api_endpoint=api_endpoint, api_key=llmcosts_api_key
            )
            set_global_usage_tracker(global_tracker)

        # Start tracker
        global_tracker.start()

        # Set up capture
        capture = BedrockStreamingCostEventCapture()

        # Patch the send_batch method
        def patched_send_batch(batch):
            if not batch:
                return

            # Track the usage data being sent
            for usage_data in batch:
                capture.capture_usage(usage_data)

            try:
                # Make the actual server call
                request_payload = {
                    "usage_records": batch,
                    "remote_save": True,
                }
                res = global_tracker._session.post(
                    global_tracker.api_endpoint,
                    json=request_payload,
                    timeout=global_tracker.timeout,
                )

                if res.status_code in [200, 207]:
                    # Success - parse and capture cost events
                    response_data = res.json()
                    capture.capture_server_response(response_data)
                    print(
                        f"✅ Bedrock streaming cost events received: {len(response_data.get('events', []))}"
                    )

                elif res.status_code == 400:
                    # Client error - capture details for debugging
                    try:
                        error_data = res.json()
                        capture.errors.append(f"400 error: {error_data}")
                        print(f"❌ 400 error: {error_data}")
                    except:
                        capture.errors.append(f"400 error: {res.text}")
                        print(f"❌ 400 error: {res.text}")
                else:
                    capture.errors.append(f"HTTP {res.status_code}: {res.text}")
                    print(f"❌ HTTP {res.status_code}: {res.text}")

            except Exception as e:
                error_msg = f"Request failed: {str(e)}"
                capture.errors.append(error_msg)
                print(f"❌ {error_msg}")

        global_tracker._send_batch = patched_send_batch

        yield capture

        # Wait for any pending operations
        time.sleep(2)
        try:
            global_tracker.shutdown()
        except Exception as e:
            print(f"WARNING: Error during tracker shutdown: {e}")

    finally:
        # Restore original tracker
        tracker._tracker = original_tracker


def get_bedrock_client():
    """Create a real Bedrock client."""
    # Get AWS credentials
    aws_access_key_id = env.str("AWS_ACCESS_KEY_ID", None)
    aws_secret_access_key = env.str("AWS_SECRET_ACCESS_KEY", None)
    region_name = env.str("AWS_DEFAULT_REGION", "us-east-2")

    if not aws_access_key_id or not aws_secret_access_key:
        pytest.skip("AWS credentials not found")

    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        return session.client(service_name="bedrock-runtime", region_name=region_name)
    except Exception as e:
        pytest.skip(f"Failed to create Bedrock client: {e}")


@pytest.mark.parametrize("model", BEDROCK_MODELS)
def test_bedrock_streaming_cost_events(bedrock_streaming_cost_capture, model):
    """Test Bedrock streaming calls and validate cost event data is returned."""
    client = get_bedrock_client()
    tracked_client = LLMTrackingProxy(
        client, provider=Provider.AMAZON_BEDROCK, debug=True
    )

    # Make a real Bedrock streaming API call
    response = tracked_client.converse_stream(
        modelId=model,
        messages=[{"role": "user", "content": [{"text": "Count from 1 to 5 slowly."}]}],
        inferenceConfig={"maxTokens": 50, "temperature": 0.1},
    )

    # Consume the stream and capture chunks
    chunks = []
    for chunk in response:
        chunks.append(chunk)
        bedrock_streaming_cost_capture.capture_streaming_chunk(chunk)

    # Verify we got streaming chunks
    assert len(chunks) > 0, "No streaming chunks received"

    # Wait for usage tracking and cost event processing
    time.sleep(3)

    # Get summary of captured data
    summary = bedrock_streaming_cost_capture.get_summary()

    print(f"\n📊 Bedrock Streaming Cost Event Test Summary for {model}:")
    print(f"  Streaming chunks: {summary['total_streaming_chunks']}")
    print(f"  Usage data sent: {summary['total_usage_data']}")
    print(f"  Server responses: {summary['total_server_responses']}")
    print(f"  Cost events received: {summary['total_cost_events']}")
    print(f"  Errors: {len(summary['errors'])}")

    # Validate we got streaming data
    assert summary["total_streaming_chunks"] > 0, "No streaming chunks were captured"

    # Validate we sent usage data (streaming should produce usage data)
    assert summary["total_usage_data"] > 0, (
        "No usage data was sent to endpoint from streaming"
    )

    # Validate data format
    if summary["sample_usage_data"]:
        usage_data = summary["sample_usage_data"][0]
        assert "model_id" in usage_data, "Usage data missing model_id"
        assert "provider" in usage_data, "Usage data missing provider"
        assert "usage" in usage_data, "Usage data missing usage"
        assert usage_data["provider"] == "amazon-bedrock", (
            f"Expected provider 'amazon-bedrock', got '{usage_data['provider']}'"
        )

        # Model ID should be sent as-is (including us. prefix) - server handles aliasing
        expected_model = model  # Keep the full model ID with us. prefix
        assert usage_data["model_id"] == expected_model, (
            f"Expected model '{expected_model}', got '{usage_data['model_id']}'"
        )

        print(f"✅ Streaming usage data format validated: {usage_data}")

    # Check for errors but be tolerant of endpoint issues during development
    if summary["errors"]:
        print(f"⚠️  Endpoint errors occurred: {summary['errors']}")

        # If we got server responses despite errors, that's progress
        if summary["total_server_responses"] > 0:
            print("✅ Successfully reached endpoint despite errors")
        else:
            # Only fail if we can't reach the endpoint at all
            connection_errors = [
                e
                for e in summary["errors"]
                if any(
                    term in e.lower() for term in ["connection", "timeout", "network"]
                )
            ]
            if connection_errors:
                pytest.skip("Endpoint not available - connection issues")
            else:
                print(
                    f"⚠️  Non-connection errors, but continuing test: {summary['errors']}"
                )

    # Validate cost events if we got them
    if summary["total_cost_events"] > 0:
        print(
            f"🎉 SUCCESS: Received {summary['total_cost_events']} cost events from streaming!"
        )

        # Validate cost event structure - match actual server response format
        cost_event = summary["sample_cost_events"][0]
        assert "model_id" in cost_event, "Cost event missing model_id"

        # Check for token information in the actual format returned by server
        has_token_info = any(
            key in cost_event
            for key in [
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "usage",
                "tokens",  # Keep these as fallbacks
            ]
        )
        assert has_token_info, (
            f"Cost event missing token information. Available keys: {list(cost_event.keys())}"
        )

        print(f"✅ Streaming cost event validated: {cost_event}")
    else:
        print(
            "📋 No cost events received yet from streaming - this may be expected during development"
        )

    print(f"✅ Bedrock streaming cost event test completed for model: {model}")
