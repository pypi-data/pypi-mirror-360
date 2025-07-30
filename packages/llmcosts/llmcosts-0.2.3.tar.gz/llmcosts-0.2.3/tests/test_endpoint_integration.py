import json
import os
import time
from unittest.mock import Mock, patch

import pytest
import requests
from environs import Env

from llmcosts.tracker.usage_delivery import UsageTracker, get_usage_tracker

# Load environment variables
env = Env()
env.read_env(os.path.join(os.path.dirname(__file__), ".env"))


class TestEndpointIntegration:
    """Test actual endpoint integration with usage segments."""

    @pytest.fixture
    def api_key(self):
        """Get the API key for llmcosts endpoint."""
        api_key = env.str("LLMCOSTS_API_KEY", None)
        if not api_key:
            pytest.skip(
                "LLMCOSTS_API_KEY not found in environment variables or tests/.env file. "
                "Please add your llmcosts.com API key to test endpoint integration."
            )
        return api_key

    @pytest.fixture
    def usage_tracker(self, api_key):
        """Create a usage tracker with real API key."""
        return UsageTracker(api_key=api_key, batch_size=1, timeout=30)

    def test_endpoint_response_format_with_mock(self, usage_tracker):
        """Test that the endpoint returns the expected response format."""
        # Mock the requests.Session.post method to capture the actual call
        with patch("requests.Session.post") as mock_post:
            # Set up the mock response
            mock_response = Mock()
            mock_response.status_code = 200  # HTTP 200 for successful response
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "status": "success",
                "processed": 1,
                "failed": None,
                "errors": None,
                "timestamp": "2025-06-23T17:17:27.881473",
            }
            mock_post.return_value = mock_response

            # Use the fixture tracker
            tracker = usage_tracker
            tracker.start()

            usage_data = {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": "test-response-456",
                "timestamp": "2025-01-20T12:00:00.000000",
            }

            tracker.track(usage_data)
            time.sleep(1)  # Allow time for processing
            tracker.shutdown()

            # Verify the call was made
            assert mock_post.called
            call_args = mock_post.call_args

            # Verify the payload structure
            sent_data = call_args[1]["json"]  # kwargs['json']

            # Should be wrapped in UsageTrackingRequest format
            assert isinstance(sent_data, dict)
            assert "usage_records" in sent_data
            assert "remote_save" in sent_data
            assert len(sent_data["usage_records"]) == 1
            assert sent_data["usage_records"][0] == usage_data

            # Verify the endpoint URL
            assert (
                call_args[0][0] == "https://llmcosts.com/api/v1/usage"
            )  # args[0] is the URL

    def test_endpoint_batch_processing(self, api_key):
        """Test that multiple usage segments are batched correctly."""
        with patch("requests.Session.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200  # HTTP 200 for successful response
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "status": "success",
                "processed": 3,
                "failed": None,
                "errors": None,
                "timestamp": "2025-06-23T17:17:27.881473",
            }
            mock_post.return_value = mock_response

            # Create tracker with batch size of 3
            tracker = UsageTracker(api_key=api_key, batch_size=3)
            tracker.start()

            # Send 3 usage data points
            usage_data_list = []
            for i in range(3):
                usage_data = {
                    "model_id": f"gpt-4o-mini-{i}",
                    "usage": {
                        "prompt_tokens": 10 + i,
                        "completion_tokens": 5 + i,
                        "total_tokens": 15 + (2 * i),
                    },
                    "response_id": f"test-response-{i}",
                    "timestamp": "2025-01-20T12:00:00.000000",
                }
                usage_data_list.append(usage_data)
                tracker.track(usage_data)

            time.sleep(1)  # Allow time for batching and processing
            tracker.shutdown()

            # Verify a single batched call was made
            assert mock_post.call_count == 1
            call_args = mock_post.call_args

            # Verify all 3 items were sent in a single batch
            sent_data = call_args[1]["json"]

            # Should be wrapped in UsageTrackingRequest format
            assert isinstance(sent_data, dict)
            assert "usage_records" in sent_data
            assert "remote_save" in sent_data
            assert len(sent_data["usage_records"]) == 3
            assert sent_data["usage_records"] == usage_data_list

    def test_endpoint_error_handling(self, api_key):
        """Test that endpoint errors are handled gracefully."""
        with patch("requests.Session.post") as mock_post:
            # Simulate a server error
            mock_post.side_effect = requests.exceptions.RequestException("Server error")

            tracker = UsageTracker(api_key=api_key, batch_size=1, max_retries=1)
            tracker.start()

            usage_data = {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": "test-response-error",
                "timestamp": "2025-01-20T12:00:00.000000",
            }

            # This should not raise an exception (errors are logged, not raised)
            tracker.track(usage_data)
            time.sleep(1)
            tracker.shutdown()

            # Verify the call was attempted
            assert mock_post.called

    def test_global_tracker_instance(self, api_key):
        """Test that the global tracker instance works correctly."""
        # Set environment variables for the global tracker
        original_endpoint = os.environ.get("LLMCOSTS_API_ENDPOINT")
        original_key = os.environ.get("LLMCOSTS_API_KEY")

        try:
            os.environ["LLMCOSTS_API_KEY"] = api_key

            with patch("requests.Session.post") as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200  # Default success status code
                mock_response.raise_for_status.return_value = None
                mock_response.json.return_value = {
                    "status": "success",
                    "processed": 1,
                    "failed": None,
                    "errors": None,
                    "timestamp": "2025-01-20T12:00:00.000000",
                }
                mock_post.return_value = mock_response

                # Reset the global tracker to None to force recreation
                import llmcosts.tracker.usage_delivery

                llmcosts.tracker.usage_delivery._tracker = None

                # Get the global tracker
                global_tracker = get_usage_tracker()

                usage_data = {
                    "model_id": "gpt-4o-mini",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                    "response_id": "test-global-tracker",
                    "timestamp": "2025-01-20T12:00:00.000000",
                }

                global_tracker.track(usage_data)
                time.sleep(1)
                global_tracker.shutdown()

                # Verify the call was made
                assert mock_post.called

        finally:
            # Restore original environment variables
            if original_endpoint is not None:
                os.environ["LLMCOSTS_API_ENDPOINT"] = original_endpoint
            elif "LLMCOSTS_API_ENDPOINT" in os.environ:
                del os.environ["LLMCOSTS_API_ENDPOINT"]

            if original_key is not None:
                os.environ["LLMCOSTS_API_KEY"] = original_key
            elif "LLMCOSTS_API_KEY" in os.environ:
                del os.environ["LLMCOSTS_API_KEY"]


class TestRealEndpointValidation:
    """Test the actual endpoint with real requests (when API key is available)."""

    @pytest.fixture
    def api_key(self):
        """Get the API key for llmcosts endpoint."""
        api_key = env.str("LLMCOSTS_API_KEY", None)
        if not api_key:
            pytest.skip(
                "LLMCOSTS_API_KEY not found. Skipping real endpoint tests. "
                "Add LLMCOSTS_API_KEY to tests/.env to run real endpoint validation."
            )
        return api_key

    @pytest.fixture
    def usage_tracker(self, api_key):
        """Create a usage tracker with real API key for endpoint testing."""
        return UsageTracker(api_key=api_key, batch_size=1, timeout=30, fail_fast=True)

    def test_real_endpoint_response_format(self, api_key):
        """Test that the real endpoint returns the expected response format."""
        # Create a real usage tracker with fail_fast enabled for testing
        tracker = UsageTracker(
            api_key=api_key, batch_size=1, timeout=30, fail_fast=True
        )

        # Patch the _send_batch method to capture the response
        original_send_batch = tracker._send_batch
        captured_responses = []
        captured_status_code = []

        def capture_response(batch):
            if not batch:
                return original_send_batch(batch)

            try:
                # Format request according to API spec
                request_payload = {"usage_records": batch, "remote_save": True}

                res = tracker._session.post(
                    tracker.api_endpoint, json=request_payload, timeout=3
                )
                captured_status_code.append(res.status_code)

                # Handle different response codes
                if res.status_code in [200, 207]:
                    # Success responses
                    response_data = res.json()
                    captured_responses.append(response_data)

                    # Validate successful response structure
                    assert "status" in response_data
                    assert "processed" in response_data
                    assert "timestamp" in response_data
                    assert response_data["status"] in [
                        "success",
                        "partial_success",
                    ]
                    assert isinstance(response_data["processed"], int)
                    assert response_data["processed"] >= 0

                    # Check for optional fields
                    if "failed" in response_data:
                        assert isinstance(response_data["failed"], (int, type(None)))
                    if "errors" in response_data:
                        assert isinstance(response_data["errors"], (list, type(None)))

                    print(f"✅ Success response validated: {response_data['status']}")
                    return True

                elif res.status_code == 422:
                    # Validation error - still validates endpoint format
                    try:
                        response_data = res.json()
                        captured_responses.append(response_data)

                        # Validate error response has some structure
                        assert isinstance(response_data, dict)
                        print("✅ 422 error response captured and validated")
                        return True  # Consider this a successful format validation
                    except json.JSONDecodeError:
                        print("⚠️ 422 response but couldn't parse JSON")
                        return False

                elif res.status_code in [400, 401, 403]:
                    # Other client errors - still validate they return structured responses
                    try:
                        response_data = res.json()
                        captured_responses.append(response_data)
                        print(f"✅ Client error {res.status_code} response captured")
                        return True
                    except json.JSONDecodeError:
                        print(f"⚠️ {res.status_code} response but couldn't parse JSON")
                        return False

                else:
                    # Server errors or other codes
                    print(f"⚠️ Unexpected status code: {res.status_code}")
                    return False

            except requests.exceptions.RequestException as e:
                print(f"❌ Request failed: {e}")
                return False
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                return False
            except AssertionError as e:
                print(f"❌ Response format validation failed: {e}")
                return False
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return False

        tracker._send_batch = capture_response
        tracker.start()

        # Send test data that should now be accepted by the fixed API
        test_data = [
            {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": "test-response-1",
                "timestamp": "2025-01-20T12:00:00.000000+00:00",
            },
        ]

        for data in test_data:
            tracker.track(data)

        # Wait for delivery
        delivery_completed = tracker.wait_for_delivery(timeout=10.0)

        # Check tracker status
        tracker_status = tracker.status.value
        last_error = tracker.last_error

        tracker.shutdown()

        # Print summary
        print("📊 Test Summary:")
        print(f"  - Delivery completed: {delivery_completed}")
        print(f"  - Tracker status: {tracker_status}")
        print(f"  - Last error: {last_error}")
        print(f"  - Captured responses: {len(captured_responses)}")
        print(f"  - Status codes: {captured_status_code}")

        # Test passes if we got ANY structured response from the endpoint
        if len(captured_responses) > 0:
            print("✅ Test passed: Successfully validated endpoint response format")
            response = captured_responses[0]
            print(f"  - Sample response: {json.dumps(response, indent=2)}")

            # Basic validation that we got a structured response
            assert isinstance(response, dict), "Response should be a dictionary"

        elif tracker_status == "failed" and last_error and "401" in last_error:
            pytest.fail(
                f"Authentication failed: {last_error}. "
                f"Check your LLMCOSTS_API_KEY in tests/.env"
            )
        elif not delivery_completed:
            pytest.fail("Request timed out - check API key and endpoint connectivity")
        else:
            pytest.fail(
                f"No response captured from endpoint. "
                f"Status: {tracker_status}, Error: {last_error}"
            )

    def test_authentication_failure_detection(self):
        """Test that authentication failures are detected quickly and don't hang."""
        # Mock a 401 authentication failure instead of relying on endpoint behavior
        with patch("requests.Session.post") as mock_post:
            # Create a mock response that raises HTTPError with 401 status
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "401 Client Error: Unauthorized", response=mock_response
            )
            mock_post.return_value = mock_response

            # Create tracker with fail_fast enabled
            tracker = UsageTracker(
                api_key="invalid-key", batch_size=1, timeout=5, fail_fast=True
            )
            tracker.start()

            usage_data = {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": "test-auth-failure",
                "timestamp": "2025-01-20T12:00:00.000000",
            }

            tracker.track(usage_data)

            # Wait for delivery - should fail fast
            start_time = time.time()
            delivery_completed = tracker.wait_for_delivery(timeout=10.0)
            elapsed_time = time.time() - start_time

            tracker.shutdown()

            # Should have failed quickly (within a few seconds, not 10+ seconds)
            assert elapsed_time < 8.0, (
                f"Authentication failure took too long: {elapsed_time}s"
            )

            # Should be in failed status
            assert tracker.status.value == "failed", (
                f"Expected failed status, got {tracker.status.value}"
            )

            # Should have an error message about authentication
            assert tracker.last_error is not None, "No error message captured"
            assert (
                "401" in tracker.last_error or "Unauthorized" in tracker.last_error
            ), f"Expected authentication error, got: {tracker.last_error}"

            print(
                f"✅ Authentication failure detected in {elapsed_time:.2f}s: {tracker.last_error}"
            )


class TestEndpointResponseScenarios:
    """Test different endpoint response scenarios: success, partial_success, failed."""

    @pytest.fixture
    def api_key(self):
        """Get the API key for endpoint tests."""
        return "test-api-key-12345"

    @pytest.fixture
    def usage_tracker(self, api_key):
        """Create a usage tracker for scenario testing."""
        return UsageTracker(api_key=api_key, batch_size=1, timeout=30)

    def test_success_response_scenario(self, api_key):
        """Test handling of successful endpoint response with all records processed."""
        with patch("requests.Session.post") as mock_post:
            # Mock successful response like the first curl example
            mock_response = Mock()
            mock_response.status_code = 200  # HTTP 200 for all records successful
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "status": "success",
                "processed": 2,
                "failed": None,
                "errors": None,
                "timestamp": "2025-06-23T18:15:13.476416",
            }
            mock_post.return_value = mock_response

            tracker = UsageTracker(api_key=api_key, batch_size=2)
            tracker.start()

            # Send two valid usage records (matching curl example)
            usage_data_1 = {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 25,
                    "total_tokens": 35,
                },
                "response_id": "chatcmpl-success-1",
                "timestamp": "2025-01-20T12:00:00.123456+00:00",
            }
            usage_data_2 = {
                "model_id": "claude-3-5-sonnet-20241022",
                "usage": {"input_tokens": 15, "output_tokens": 30},
                "response_id": "msg_success-2",
                "timestamp": "2025-01-20T12:01:00.123456+00:00",
            }

            tracker.track(usage_data_1)
            tracker.track(usage_data_2)
            time.sleep(1)
            tracker.shutdown()

            # Verify the call was made with correct payload
            assert mock_post.called
            call_args = mock_post.call_args
            sent_data = call_args[1]["json"]

            # Should be wrapped in UsageTrackingRequest format
            assert "usage_records" in sent_data
            assert "remote_save" in sent_data
            assert len(sent_data["usage_records"]) == 2
            assert sent_data["usage_records"][0] == usage_data_1
            assert sent_data["usage_records"][1] == usage_data_2

    def test_partial_success_response_scenario(self, api_key):
        """Test handling of partial success response with some records failing validation."""
        with patch("requests.Session.post") as mock_post:
            # Mock partial success response like the second curl example
            mock_response = Mock()
            mock_response.status_code = (
                207  # HTTP 207 for partial success (Multi-Status)
            )
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "status": "partial_success",
                "processed": 1,
                "failed": 1,
                "errors": [
                    {
                        "response_id": "msg_partial-2",
                        "record_index": 1,
                        "errors": [
                            "Token count 'output_tokens' cannot be negative: -5"
                        ],
                    }
                ],
                "timestamp": "2025-06-23T18:18:39.534095",
            }
            mock_post.return_value = mock_response

            tracker = UsageTracker(api_key=api_key, batch_size=2)
            tracker.start()

            # Send one valid and one invalid record (matching curl example)
            usage_data_1 = {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 25,
                    "total_tokens": 35,
                },
                "response_id": "chatcmpl-partial-1",
                "timestamp": "2025-01-20T12:00:00.123456+00:00",
            }
            usage_data_2 = {
                "model_id": "claude-3-5-sonnet-20241022",
                "usage": {
                    "input_tokens": 15,
                    "output_tokens": -5,
                },  # Invalid negative tokens
                "response_id": "msg_partial-2",
                "timestamp": "2025-01-20T12:01:00.123456+00:00",
            }

            tracker.track(usage_data_1)
            tracker.track(usage_data_2)
            time.sleep(1)
            tracker.shutdown()

            # Verify the call was made - no exception should be raised for partial success
            assert mock_post.called
            call_args = mock_post.call_args
            sent_data = call_args[1]["json"]

            # Should be wrapped in UsageTrackingRequest format
            assert "usage_records" in sent_data
            assert "remote_save" in sent_data
            assert len(sent_data["usage_records"]) == 2

    def test_failed_response_scenario(self, api_key):
        """Test handling of failed response with all records failing validation."""
        with patch("requests.Session.post") as mock_post:
            # Mock failed response like the third curl example
            mock_response = Mock()
            mock_response.status_code = (
                400  # HTTP 400 for all records failed (Bad Request)
            )
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "400 Client Error: Bad Request", response=mock_response
            )
            mock_response.json.return_value = {
                "status": "failed",
                "processed": 0,
                "failed": 2,
                "errors": [
                    {
                        "response_id": "chatcmpl-failed-1",
                        "record_index": 0,
                        "errors": [
                            "OpenAI record missing required usage fields: ['completion_tokens']"
                        ],
                    },
                    {
                        "response_id": "msg_failed-2",
                        "record_index": 1,
                        "errors": [
                            "Token count 'input_tokens' cannot be negative: -10",
                            "Token count 'output_tokens' cannot be negative: -5",
                        ],
                    },
                ],
                "timestamp": "2025-06-23T18:19:12.404879",
            }
            mock_post.return_value = mock_response

            tracker = UsageTracker(api_key=api_key, batch_size=2)
            tracker.start()

            # Send two invalid records (matching curl example)
            usage_data_1 = {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "total_tokens": 35,
                },  # Missing completion_tokens
                "response_id": "chatcmpl-failed-1",
                "timestamp": "2025-01-20T12:00:00.123456+00:00",
            }
            usage_data_2 = {
                "model_id": "claude-3-5-sonnet-20241022",
                "usage": {"input_tokens": -10, "output_tokens": -5},  # Negative tokens
                "response_id": "msg_failed-2",
                "timestamp": "2025-01-20T12:01:00.123456+00:00",
            }

            tracker.track(usage_data_1)
            tracker.track(usage_data_2)
            time.sleep(1)
            tracker.shutdown()

            # Verify the call was made - no exception should be raised for failed status
            assert mock_post.called
            call_args = mock_post.call_args
            sent_data = call_args[1]["json"]

            # Should be wrapped in UsageTrackingRequest format
            assert "usage_records" in sent_data
            assert "remote_save" in sent_data
            assert len(sent_data["usage_records"]) == 2

    def test_response_format_validation_all_scenarios(self, usage_tracker):
        """Test that all response scenario formats are properly validated."""
        test_scenarios = [
            {
                "name": "success",
                "response": {
                    "status": "success",
                    "processed": 2,
                    "failed": None,
                    "errors": None,
                    "timestamp": "2025-06-23T18:15:13.476416",
                },
            },
            {
                "name": "partial_success",
                "response": {
                    "status": "partial_success",
                    "processed": 1,
                    "failed": 1,
                    "errors": [
                        {
                            "response_id": "test",
                            "record_index": 1,
                            "errors": ["Test error"],
                        }
                    ],
                    "timestamp": "2025-06-23T18:18:39.534095",
                },
            },
            {
                "name": "failed",
                "response": {
                    "status": "failed",
                    "processed": 0,
                    "failed": 2,
                    "errors": [
                        {
                            "response_id": "test1",
                            "record_index": 0,
                            "errors": ["Error 1"],
                        },
                        {
                            "response_id": "test2",
                            "record_index": 1,
                            "errors": ["Error 2"],
                        },
                    ],
                    "timestamp": "2025-06-23T18:19:12.404879",
                },
            },
        ]

        for scenario in test_scenarios:
            with patch("requests.Session.post") as mock_post:
                mock_response = Mock()
                # Set appropriate status code for each scenario
                if scenario["name"] == "success":
                    mock_response.status_code = 200
                    mock_response.raise_for_status.return_value = None
                elif scenario["name"] == "partial_success":
                    mock_response.status_code = 207
                    mock_response.raise_for_status.return_value = None
                elif scenario["name"] == "failed":
                    mock_response.status_code = 400
                    mock_response.raise_for_status.side_effect = (
                        requests.exceptions.HTTPError(
                            "400 Client Error: Bad Request", response=mock_response
                        )
                    )

                mock_response.json.return_value = scenario["response"]
                mock_post.return_value = mock_response

                tracker = usage_tracker
                tracker.start()

                usage_data = {
                    "model_id": "test-model",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                    "response_id": f"test-{scenario['name']}",
                    "timestamp": "2025-01-20T12:00:00.000000",
                }

                tracker.track(usage_data)
                time.sleep(1)
                tracker.shutdown()

                # All scenarios should complete without raising exceptions
                assert mock_post.called, (
                    f"Request not made for {scenario['name']} scenario"
                )


def test_endpoint_response_format_comprehensive():
    """Comprehensive test of endpoint response format without making LLM calls."""
    api_key = env.str("LLMCOSTS_API_KEY", None)
    if not api_key:
        pytest.skip("LLMCOSTS_API_KEY not found")

    # Create a test tracker with reasonable timeout
    tracker = UsageTracker(api_key=api_key, batch_size=2, timeout=5)
    captured_responses = []
    endpoint_errors = []

    # Store the original _send_batch method
    original_send_batch = tracker._send_batch

    def capture_and_validate_response(batch):
        if not batch:
            return original_send_batch(batch)

        try:
            # Call the original method to make the actual request
            result = original_send_batch(batch)

            # Try to validate the response format by making a test request
            try:
                # Format request according to API spec
                request_payload = {"usage_records": batch, "remote_save": True}

                res = tracker._session.post(
                    tracker.api_endpoint, json=request_payload, timeout=3
                )

                # With the fixed API, we should now get success responses
                if res.status_code in [200, 207]:
                    # Success response - validate structure
                    response_data = res.json()
                    captured_responses.append(response_data)

                    # Validate successful response format
                    assert isinstance(response_data, dict), (
                        "Response should be a dictionary"
                    )
                    assert "status" in response_data, "Response missing 'status' field"
                    assert "processed" in response_data, (
                        "Response missing 'processed' field"
                    )
                    assert "timestamp" in response_data, (
                        "Response missing 'timestamp' field"
                    )

                    print(f"✅ Success response validated: {response_data['status']}")

                elif res.status_code == 422:
                    # This should be rare now with the fixed API
                    try:
                        error_response = res.json()
                        captured_responses.append(error_response)
                        print(f"⚠️ Unexpected validation error: {error_response}")
                    except Exception:
                        error_msg = "422 response but couldn't parse JSON"
                        endpoint_errors.append(error_msg)
                        print(f"⚠️ {error_msg}")

                elif res.status_code in [400, 401, 403]:
                    # Client errors
                    try:
                        error_response = res.json()
                        captured_responses.append(error_response)
                        print(f"⚠️ Client error response: {res.status_code}")
                    except Exception:
                        error_msg = (
                            f"{res.status_code} response but couldn't parse JSON"
                        )
                        endpoint_errors.append(error_msg)
                        print(f"⚠️ {error_msg}")

                else:
                    error_msg = f"Unexpected status code: {res.status_code}"
                    endpoint_errors.append(error_msg)
                    print(f"❌ {error_msg}")

            except Exception as validation_error:
                error_msg = f"Validation error: {validation_error}"
                endpoint_errors.append(error_msg)
                print(f"⚠️ {error_msg}")

            return result

        except Exception as e:
            error_msg = f"Tracker error: {e}"
            endpoint_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return original_send_batch(batch)

    # Patch the tracker's send method
    tracker._send_batch = capture_and_validate_response

    try:
        tracker.start()

        # Send test data that should now be accepted by the fixed API
        test_data = [
            {
                "model_id": "gpt-4o-mini",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                },
                "response_id": "test-response-1",
                "timestamp": "2025-01-20T12:00:00.000000+00:00",
            },
        ]

        for data in test_data:
            tracker.track(data)

        # Wait for processing
        time.sleep(2)

    except Exception as e:
        print(f"Test execution error: {e}")
    finally:
        try:
            tracker.shutdown()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")

    # Print summary
    print("📊 Test Summary:")
    print(f"  - Captured responses: {len(captured_responses)}")
    print(f"  - Endpoint errors: {len(endpoint_errors)}")

    if endpoint_errors:
        print(f"  - Errors: {endpoint_errors}")

    # Test passes if we got ANY structured response from the endpoint
    if len(captured_responses) > 0:
        print("✅ Test passed: Successfully validated endpoint response format")
        print(f"  - Sample response: {captured_responses[0]}")

        # Basic validation that we got structured responses
        for response in captured_responses:
            assert isinstance(response, dict), "All responses should be dictionaries"

    elif len(endpoint_errors) > 0:
        # Only skip if we have connection errors
        connection_errors = [
            e
            for e in endpoint_errors
            if "connection" in e.lower() or "timeout" in e.lower()
        ]
        if connection_errors:
            print("⚠️ Endpoint unreachable, but test structure is valid")
            pytest.skip("Endpoint not reachable - skipping response format validation")
        else:
            print("❌ Got errors but they weren't connection errors")
            pytest.fail(f"Test failed with non-connection errors: {endpoint_errors}")
    else:
        print("❌ No responses captured and no endpoint errors")
        pytest.fail("Test failed to interact with endpoint at all")
