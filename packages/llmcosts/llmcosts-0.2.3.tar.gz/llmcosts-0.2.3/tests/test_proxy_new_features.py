"""
Test the new features of LLMTrackingProxy: remote_save, context, and response_callback.
"""

from unittest.mock import MagicMock, patch

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.providers import Provider


class MockClient:
    """Mock LLM client for testing."""

    def __init__(self):
        self.usage = MagicMock()
        self.usage.prompt_tokens = 10
        self.usage.completion_tokens = 20
        self.usage.total_tokens = 30
        self.usage.model_dump.return_value = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        }
        self._is_openai_mock = True
        self.model = "test-model"
        self.id = "test-response-id"

    def chat_completion(self, **kwargs):
        """Mock chat completion method."""
        return self


class MockResponsesClient(MockClient):
    """Mock client mimicking OpenAI responses API."""

    def __init__(self):
        super().__init__()
        self.responses = self

    def __str__(self):
        return "responses"

    def create(self, **kwargs):  # noqa: D401 - mimic openai responses.create
        return self


class TestProxyNewFeatures:
    """Test the new LLMTrackingProxy features."""

    def test_remote_save_default_true(self):
        """Test that remote_save defaults to True and doesn't add the field."""
        mock_client = MockClient()

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(mock_client, provider=Provider.OPENAI)

            # Make a call
            result = proxy.chat_completion()

            # Verify the call was tracked
            assert mock_tracker.track.called
            payload = mock_tracker.track.call_args[0][0]

            # Should not contain 'remote_save' field when True (default)
            assert "remote_save" not in payload
            assert result == mock_client

    def test_remote_save_false(self):
        """Test that remote_save=False adds remote_save=False to payload."""
        mock_client = MockClient()

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client, provider=Provider.OPENAI, remote_save=False
            )

            # Make a call
            result = proxy.chat_completion()

            # Verify the call was tracked with remote_save=False
            assert mock_tracker.track.called
            payload = mock_tracker.track.call_args[0][0]

            assert payload["remote_save"] is False
            assert result == mock_client

    def test_remote_save_setter(self):
        """Test that remote_save can be changed via setter."""
        mock_client = MockClient()
        proxy = LLMTrackingProxy(
            mock_client, provider=Provider.OPENAI, remote_save=True
        )

        assert proxy.remote_save is True

        proxy.remote_save = False
        assert proxy.remote_save is False

    def test_context_added_to_payload(self):
        """Test that context is added to the payload."""
        mock_client = MockClient()
        test_context = {"user_id": "123", "session_id": "abc"}

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client, provider=Provider.OPENAI, context=test_context
            )

            # Make a call
            result = proxy.chat_completion()

            # Verify the call was tracked with context
            assert mock_tracker.track.called
            payload = mock_tracker.track.call_args[0][0]

            assert payload["context"] == test_context
            assert result == mock_client

    def test_context_setter(self):
        """Test that context can be changed via setter."""
        mock_client = MockClient()
        initial_context = {"user_id": "123"}
        new_context = {"user_id": "456", "session_id": "xyz"}

        proxy = LLMTrackingProxy(
            mock_client, provider=Provider.OPENAI, context=initial_context
        )

        assert proxy.context == initial_context

        proxy.context = new_context
        assert proxy.context == new_context

        # Test setting to None
        proxy.context = None
        assert proxy.context is None

    def test_context_is_copied(self):
        """Test that context is copied to prevent external modifications."""
        mock_client = MockClient()
        original_context = {"user_id": "123"}

        proxy = LLMTrackingProxy(
            mock_client, provider=Provider.OPENAI, context=original_context
        )

        # Modify the original context
        original_context["user_id"] = "456"

        # The proxy's context should not be affected
        assert proxy.context["user_id"] == "123"

    def test_response_callback_called(self):
        """Test that response_callback is called with the response."""
        mock_client = MockClient()
        callback_calls = []

        def test_callback(response):
            callback_calls.append(response)

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client, provider=Provider.OPENAI, response_callback=test_callback
            )

            # Make a call
            result = proxy.chat_completion()

            # Verify callback was called with the response
            assert len(callback_calls) == 1
            assert callback_calls[0] == mock_client
            assert result == mock_client

    def test_response_callback_error_handling(self, caplog):
        """Test that errors in response_callback are handled gracefully."""
        mock_client = MockClient()

        def error_callback(response):
            raise ValueError("Test error")

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client, provider=Provider.OPENAI, response_callback=error_callback
            )

            # Make a call - should not raise exception
            result = proxy.chat_completion()

            # Should still return the result despite callback error
            assert result == mock_client

            # Should log the error
            assert "Error in response callback" in caplog.text

    def test_response_callback_setter(self):
        """Test that response_callback can be changed via setter."""
        mock_client = MockClient()

        def callback1(response):
            pass

        def callback2(response):
            pass

        proxy = LLMTrackingProxy(
            mock_client, provider=Provider.OPENAI, response_callback=callback1
        )

        assert proxy.response_callback == callback1

        proxy.response_callback = callback2
        assert proxy.response_callback == callback2

        proxy.response_callback = None
        assert proxy.response_callback is None

    def test_sync_mode_setter(self):
        """Test that sync_mode can be changed via setter."""
        mock_client = MockClient()

        proxy = LLMTrackingProxy(mock_client, provider=Provider.OPENAI, sync_mode=False)
        assert proxy.sync_mode is False

        proxy.sync_mode = True
        assert proxy.sync_mode is True

    def test_combined_features(self):
        """Test using remote_save, context, and response_callback together."""
        mock_client = MockClient()
        test_context = {"user_id": "123"}
        callback_calls = []

        def test_callback(response):
            callback_calls.append(response)

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client,
                provider=Provider.OPENAI,
                remote_save=False,
                context=test_context,
                response_callback=test_callback,
            )

            # Make a call
            result = proxy.chat_completion()

            # Verify all features work together
            assert mock_tracker.track.called
            payload = mock_tracker.track.call_args[0][0]

            assert payload["remote_save"] is False  # remote_save=False
            assert payload["context"] == test_context  # context added
            assert len(callback_calls) == 1  # callback called
            assert callback_calls[0] == mock_client
            assert result == mock_client

    def test_context_changes_between_calls(self):
        """Context setter should update payloads for subsequent calls."""
        mock_client = MockClient()

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client, provider=Provider.OPENAI, context={"first": True}
            )

            # First call with initial context
            proxy.chat_completion()
            first_payload = mock_tracker.track.call_args_list[0][0][0]
            assert first_payload["context"] == {"first": True}

            # Change context and make another call
            proxy.context = {"second": True}
            proxy.chat_completion()
            second_payload = mock_tracker.track.call_args_list[1][0][0]
            assert second_payload["context"] == {"second": True}

    def test_base_url_not_in_payload_by_default(self):
        mock_client = MockClient()

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(mock_client, provider=Provider.OPENAI)

            proxy.chat_completion()
            payload = mock_tracker.track.call_args[0][0]
            assert "base_url" not in payload

    def test_base_url_added_when_set(self):
        mock_client = MockClient()

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client,
                provider=Provider.OPENAI,
                base_url="https://api.example.com/v1",
            )

            proxy.chat_completion()
            payload = mock_tracker.track.call_args[0][0]
            assert payload["base_url"] == "https://api.example.com/v1"

    def test_base_url_setter(self):
        mock_client = MockClient()
        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(mock_client, provider=Provider.OPENAI)

            assert proxy.base_url is None
            proxy.base_url = "https://api.deepseek.com/v1"
            assert proxy.base_url == "https://api.deepseek.com/v1"

            proxy.chat_completion()
            payload = mock_tracker.track.call_args[0][0]
            assert payload["base_url"] == "https://api.deepseek.com/v1"

    def test_base_url_ignored_for_responses_api(self):
        mock_client = MockResponsesClient()

        with patch("llmcosts.tracker.proxy.get_usage_tracker") as mock_get_tracker:
            mock_tracker = MagicMock()
            mock_get_tracker.return_value = mock_tracker

            proxy = LLMTrackingProxy(
                mock_client,
                provider=Provider.OPENAI,
                base_url="https://api.example.com/v1",
            )

            proxy.responses.create(model="gpt-4")
            payload = mock_tracker.track.call_args[0][0]
            assert "base_url" not in payload
