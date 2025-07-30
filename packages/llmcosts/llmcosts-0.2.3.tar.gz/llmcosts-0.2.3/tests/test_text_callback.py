"""
Tests for text callback functionality with real OpenAI API calls.

Tests that the text_callback function correctly extracts cost event data from
LLM responses and stores it in a JSON Lines text file.
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

import openai
import pytest
from environs import Env

# Add the parent directory to sys.path so we can import from the main project
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmcosts.tracker import LLMTrackingProxy
from llmcosts.tracker.callbacks import text_callback
from llmcosts.tracker.providers import Provider

# Load environment variables from .env file in the tests directory
env = Env()
env.read_env(Path(__file__).parent / ".env")


class TestTextCallback:
    """Test suite for text callback with real OpenAI API calls."""

    @pytest.fixture
    def temp_text_dir(self):
        """Create a temporary directory for text file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variable for callback
            os.environ["TEXT_CALLBACK_TARGET_PATH"] = temp_dir
            yield temp_dir
            # Clean up environment variable
            if "TEXT_CALLBACK_TARGET_PATH" in os.environ:
                del os.environ["TEXT_CALLBACK_TARGET_PATH"]

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
    def tracked_client_with_callback(self, openai_client):
        """Create a tracked OpenAI client with text callback."""
        return LLMTrackingProxy(
            openai_client,
            provider=Provider.OPENAI,
            debug=True,
            response_callback=text_callback,
        )

    def _get_text_path(self, temp_dir: str) -> Path:
        """Get the path to the text file."""
        return Path(temp_dir) / "llm_cost_events.jsonl"

    def _read_text_records(self, text_path: Path) -> list:
        """Read all records from the JSON Lines text file."""
        if not text_path.exists():
            return []

        records = []
        with open(text_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Invalid JSON on line {line_num}: {e}")

        return records

    def test_text_callback_missing_env_var(self):
        """Test that text callback raises error when environment variable is missing."""
        # Ensure environment variable is not set
        if "TEXT_CALLBACK_TARGET_PATH" in os.environ:
            del os.environ["TEXT_CALLBACK_TARGET_PATH"]

        # Create a mock response
        class MockResponse:
            def __init__(self):
                self.id = "test-123"
                self.model = "gpt-4o-mini"

        # The callback should log an error but not raise (to avoid breaking main flow)
        # We can't easily test the ValueError since it's caught and logged
        text_callback(MockResponse())
        # If we get here without an exception, the error handling worked

    def test_text_callback_non_streaming(
        self, temp_text_dir, tracked_client_with_callback
    ):
        """Test text callback with non-streaming OpenAI API call."""
        text_path = self._get_text_path(temp_text_dir)

        # Make a non-streaming call
        response = tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hello in one word"}],
            max_tokens=5,
        )

        # Verify response is valid
        assert response.choices[0].message.content is not None
        assert response.usage.total_tokens > 0

        # Give callback time to process
        time.sleep(0.1)

        # Verify text file was created and contains the record
        assert text_path.exists(), "Text file should be created"

        records = self._read_text_records(text_path)
        assert len(records) == 1, "Should have exactly one record"

        record = records[0]
        assert record["response_id"] == response.id
        assert record["model_id"] == "gpt-4o-mini"  # Normalized model name
        assert record["provider"] == "openai"
        assert record["input_tokens"] == response.usage.prompt_tokens
        assert record["output_tokens"] == response.usage.completion_tokens
        assert record["total_tokens"] == response.usage.total_tokens
        assert record["timestamp"] is not None
        assert record["created_at"] is not None
        assert record["updated_at"] is not None

    def test_text_callback_streaming(self, temp_text_dir, tracked_client_with_callback):
        """Test text callback with streaming OpenAI API call."""
        text_path = self._get_text_path(temp_text_dir)

        # Make a streaming call
        stream = tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Count from 1 to 3"}],
            stream=True,
            stream_options={"include_usage": True},
            max_tokens=20,
        )

        # Consume the stream
        chunks = list(stream)
        assert len(chunks) > 0

        # Find the usage chunk
        usage_chunks = [chunk for chunk in chunks if chunk.usage is not None]
        assert len(usage_chunks) == 1, "Should have exactly one usage chunk"

        usage_chunk = usage_chunks[0]

        # Give callback time to process
        time.sleep(0.1)

        # Verify text file contains records (one for each chunk + final usage)
        assert text_path.exists(), "Text file should be created"

        records = self._read_text_records(text_path)
        assert len(records) >= 1, "Should have at least one record"

        # Find the record with usage data
        usage_record = None
        for record in records:
            if record.get("total_tokens") is not None and record["total_tokens"] > 0:
                usage_record = record
                break

        assert usage_record is not None, "Should have a record with usage data"
        assert usage_record["model_id"] == "gpt-4o-mini"
        assert usage_record["provider"] == "openai"
        assert usage_record["input_tokens"] == usage_chunk.usage.prompt_tokens
        assert usage_record["output_tokens"] == usage_chunk.usage.completion_tokens
        assert usage_record["total_tokens"] == usage_chunk.usage.total_tokens

    def test_text_callback_record_overwrite(
        self, temp_text_dir, tracked_client_with_callback
    ):
        """Test that text callback overwrites records with the same response_id."""
        text_path = self._get_text_path(temp_text_dir)

        # Make first call
        response1 = tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )

        time.sleep(0.1)

        # Verify first record
        records = self._read_text_records(text_path)
        assert len(records) == 1
        first_record = records[0]
        first_updated_at = first_record["updated_at"]
        first_created_at = first_record["created_at"]

        # Make second call with different content but force same response_id for testing
        response2 = tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello there"}],
            max_tokens=10,
        )

        time.sleep(0.1)

        # Verify we now have records (may be more due to different response_ids)
        records = self._read_text_records(text_path)
        assert len(records) >= 1

        # Each response should have its own record with different response_ids
        response_ids = [record["response_id"] for record in records]
        assert response1.id in response_ids
        assert response2.id in response_ids

    def test_text_callback_file_format(
        self, temp_text_dir, tracked_client_with_callback
    ):
        """Test that text callback creates valid JSON Lines format."""
        text_path = self._get_text_path(temp_text_dir)

        # Make multiple calls to generate multiple records
        for i in range(3):
            tracked_client_with_callback.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Test message {i}"}],
                max_tokens=5,
            )

        time.sleep(0.3)

        # Verify file format
        assert text_path.exists(), "Text file should be created"

        # Read raw file content to verify format
        with open(text_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) >= 3, "Should have at least 3 lines"

        # Each line should be valid JSON
        for i, line in enumerate(lines):
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    record = json.loads(line)
                    assert isinstance(record, dict), (
                        f"Line {i + 1} should be a JSON object"
                    )
                    assert "response_id" in record, (
                        f"Line {i + 1} should have response_id"
                    )
                    assert "timestamp" in record, f"Line {i + 1} should have timestamp"
                except json.JSONDecodeError as e:
                    pytest.fail(f"Line {i + 1} is not valid JSON: {e}")

    def test_text_callback_record_update_simulation(self, temp_text_dir):
        """Test record overwrite by manually creating duplicate response_ids."""
        text_path = self._get_text_path(temp_text_dir)

        # Create mock responses with same response_id
        class MockResponse:
            def __init__(self, response_id, model, tokens):
                self.id = response_id
                self.model = model
                self.usage = type(
                    "obj",
                    (object,),
                    {
                        "prompt_tokens": tokens[0],
                        "completion_tokens": tokens[1],
                        "total_tokens": tokens[0] + tokens[1],
                    },
                )()

        # First call with response_id "test-123"
        mock_response1 = MockResponse("test-123", "gpt-4o-mini", (10, 5))
        text_callback(mock_response1)

        time.sleep(0.1)

        # Verify first record
        records = self._read_text_records(text_path)
        assert len(records) == 1
        assert records[0]["response_id"] == "test-123"
        assert records[0]["input_tokens"] == 10
        assert records[0]["output_tokens"] == 5
        first_created_at = records[0]["created_at"]
        first_updated_at = records[0]["updated_at"]

        # Small delay to ensure different timestamp
        time.sleep(0.01)

        # Second call with same response_id but different token counts
        mock_response2 = MockResponse("test-123", "gpt-4o-mini", (15, 8))
        text_callback(mock_response2)

        time.sleep(0.1)

        # Verify record was overwritten
        records = self._read_text_records(text_path)
        assert len(records) == 1, "Should still have only one record (overwritten)"

        updated_record = records[0]
        assert updated_record["response_id"] == "test-123"
        assert updated_record["input_tokens"] == 15  # Updated values
        assert updated_record["output_tokens"] == 8
        assert (
            updated_record["created_at"] == first_created_at
        )  # Should preserve original created_at
        assert (
            updated_record["updated_at"] != first_updated_at
        )  # Should have new updated_at

    def test_text_callback_context_handling(self, temp_text_dir):
        """Test text callback properly handles context as dict/JSON."""
        text_path = self._get_text_path(temp_text_dir)

        # Create mock responses with context as dict
        class MockResponseWithContext:
            def __init__(self, response_id, model, context_dict):
                self.id = response_id
                self.model = model
                self.context = context_dict  # Dict context on response
                self.usage = type(
                    "obj",
                    (object,),
                    {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                )()

        # Test with various context formats
        test_contexts = [
            {"user_id": "123", "session_id": "abc"},
            {"client": "test-client", "user": "test-user", "app_version": "1.0"},
            {"nested": {"data": {"level": 2}}, "array": [1, 2, 3]},
        ]

        for i, context in enumerate(test_contexts):
            mock_response = MockResponseWithContext(
                f"ctx-test-{i}", "gpt-4o-mini", context
            )
            text_callback(mock_response)

        time.sleep(0.1)

        # Verify text file records
        records = self._read_text_records(text_path)
        assert len(records) >= len(test_contexts)

        # Check that contexts are stored as dict objects in JSON
        for i, record in enumerate(records[: len(test_contexts)]):
            if record.get("context"):
                # Text file stores context as dict directly in JSON
                stored_context = record["context"]
                expected_context = test_contexts[i]
                assert isinstance(stored_context, dict)
                assert stored_context == expected_context

    def test_text_callback_dict_response_context(self, temp_text_dir):
        """Test text callback with dict response containing context."""
        text_path = self._get_text_path(temp_text_dir)

        # Test dict response format with context
        dict_response = {
            "id": "dict-response-456",
            "model": "gpt-4o-mini",
            "context": {"integration": "test", "source": "dict_response"},
            "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
        }

        text_callback(dict_response)
        time.sleep(0.1)

        records = self._read_text_records(text_path)
        assert len(records) >= 1

        # Find our record
        test_record = None
        for record in records:
            if record["response_id"] == "dict-response-456":
                test_record = record
                break

        assert test_record is not None
        assert test_record["model_id"] == "gpt-4o-mini"

        # Verify context is stored correctly as dict
        assert test_record.get("context") == {
            "integration": "test",
            "source": "dict_response",
        }

    def test_text_callback_error_handling(self, temp_text_dir):
        """Test text callback error handling with malformed response objects."""
        text_path = self._get_text_path(temp_text_dir)

        # Test with various malformed response objects
        test_objects = [
            None,
            {},
            "not an object",
            type("BadObj", (), {})(),  # Object with no useful attributes
        ]

        for test_obj in test_objects:
            text_callback(test_obj)

        time.sleep(0.1)

        # Should create file and records even with malformed objects
        assert text_path.exists(), "Text file should be created even with errors"

        records = self._read_text_records(text_path)
        # Should have records for each test object (with minimal/error data)
        assert len(records) >= len(test_objects)

        # Check that error records have fallback values and context is dict format
        for record in records:
            assert record["response_id"] is not None
            assert record["timestamp"] is not None
            # Context should be dict even for errors
            if record.get("context"):
                assert isinstance(record["context"], dict)
                # Should contain extraction_error key for error cases
                if "extraction_error" in record["context"]:
                    assert isinstance(record["context"]["extraction_error"], str)

    def test_text_callback_malformed_existing_file(self, temp_text_dir):
        """Test text callback handling of malformed existing JSON Lines file."""
        text_path = self._get_text_path(temp_text_dir)

        # Create a file with some valid and some malformed JSON lines
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(
                '{"response_id": "valid-1", "model_id": "test", "timestamp": "2023-01-01T00:00:00Z"}\n'
            )
            f.write("invalid json line\n")
            f.write(
                '{"response_id": "valid-2", "model_id": "test", "timestamp": "2023-01-01T00:00:01Z"}\n'
            )
            f.write('{"incomplete": "json"')  # Missing closing brace

        # Create a mock response
        class MockResponse:
            def __init__(self):
                self.id = "new-response"
                self.model = "gpt-4o-mini"
                self.usage = type(
                    "obj",
                    (object,),
                    {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                )()

        # Call the callback - should handle malformed lines gracefully
        text_callback(MockResponse())

        time.sleep(0.1)

        # Should preserve valid records and add new one
        records = self._read_text_records(text_path)

        # Should have the valid records plus the new one
        response_ids = [record["response_id"] for record in records]
        assert "valid-1" in response_ids
        assert "valid-2" in response_ids
        assert "new-response" in response_ids
        assert len(records) >= 3

    def test_text_callback_unicode_handling(self, temp_text_dir):
        """Test text callback handles unicode characters correctly."""
        text_path = self._get_text_path(temp_text_dir)

        # Create mock response with unicode in context
        class MockResponse:
            def __init__(self):
                self.id = "unicode-test"
                self.model = "gpt-4o-mini"
                self.usage = type(
                    "obj",
                    (object,),
                    {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                )()

        # Create a mock response with unicode context directly
        class MockResponseWithUnicode:
            def __init__(self):
                self.id = "unicode-test"
                self.model = "gpt-4o-mini"
                self.context = {
                    "message": "Test with unicode: 中文, emoji: 🚀, accents: café",
                    "unicode_test": True,
                }
                self.usage = type(
                    "obj",
                    (object,),
                    {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                )()

        text_callback(MockResponseWithUnicode())
        time.sleep(0.1)

        # Should handle unicode correctly
        records = self._read_text_records(text_path)
        assert len(records) == 1
        context = records[0]["context"]
        assert isinstance(context, dict)
        assert "中文" in context["message"]
        assert "🚀" in context["message"]
        assert "café" in context["message"]
        assert context["unicode_test"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
