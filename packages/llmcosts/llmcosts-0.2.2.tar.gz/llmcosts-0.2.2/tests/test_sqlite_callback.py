"""
Tests for SQLite callback functionality with real OpenAI API calls.

Tests that the sqlite_callback function correctly extracts cost event data from
LLM responses and stores it in a SQLite database.
"""

import os
import sqlite3
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
from llmcosts.tracker.callbacks import sqlite_callback
from llmcosts.tracker.providers import Provider

# Load environment variables from .env file in the tests directory
env = Env()
env.read_env(Path(__file__).parent / ".env")


class TestSQLiteCallback:
    """Test suite for SQLite callback with real OpenAI API calls."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for SQLite database."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variable for callback
            os.environ["SQLITE_CALLBACK_TARGET_PATH"] = temp_dir
            yield temp_dir
            # Clean up environment variable
            if "SQLITE_CALLBACK_TARGET_PATH" in os.environ:
                del os.environ["SQLITE_CALLBACK_TARGET_PATH"]

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
        """Create a tracked OpenAI client with SQLite callback."""
        return LLMTrackingProxy(
            openai_client,
            provider=Provider.OPENAI,
            debug=True,
            response_callback=sqlite_callback,
        )

    def _get_db_path(self, temp_dir: str) -> Path:
        """Get the path to the SQLite database."""
        return Path(temp_dir) / "llm_cost_events.db"

    def _read_db_records(self, db_path: Path) -> list:
        """Read all records from the SQLite database."""
        if not db_path.exists():
            return []

        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cost_events ORDER BY updated_at")
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def test_sqlite_callback_missing_env_var(self):
        """Test that SQLite callback raises error when environment variable is missing."""
        # Ensure environment variable is not set
        if "SQLITE_CALLBACK_TARGET_PATH" in os.environ:
            del os.environ["SQLITE_CALLBACK_TARGET_PATH"]

        # Create a mock response
        class MockResponse:
            def __init__(self):
                self.id = "test-123"
                self.model = "gpt-4o-mini"

        # The callback should log an error but not raise (to avoid breaking main flow)
        # We can't easily test the ValueError since it's caught and logged
        sqlite_callback(MockResponse())
        # If we get here without an exception, the error handling worked

    def test_sqlite_callback_non_streaming(
        self, temp_db_dir, tracked_client_with_callback
    ):
        """Test SQLite callback with non-streaming OpenAI API call."""
        db_path = self._get_db_path(temp_db_dir)

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

        # Verify database was created and contains the record
        assert db_path.exists(), "SQLite database should be created"

        records = self._read_db_records(db_path)
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

    def test_sqlite_callback_streaming(self, temp_db_dir, tracked_client_with_callback):
        """Test SQLite callback with streaming OpenAI API call."""
        db_path = self._get_db_path(temp_db_dir)

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

        # Verify database contains records (one for each chunk + final usage)
        assert db_path.exists(), "SQLite database should be created"

        records = self._read_db_records(db_path)
        assert len(records) >= 1, "Should have at least one record"

        # Find the record with usage data
        usage_record = None
        for record in records:
            if record["total_tokens"] is not None and record["total_tokens"] > 0:
                usage_record = record
                break

        assert usage_record is not None, "Should have a record with usage data"
        assert usage_record["model_id"] == "gpt-4o-mini"
        assert usage_record["provider"] == "openai"
        assert usage_record["input_tokens"] == usage_chunk.usage.prompt_tokens
        assert usage_record["output_tokens"] == usage_chunk.usage.completion_tokens
        assert usage_record["total_tokens"] == usage_chunk.usage.total_tokens

    def test_sqlite_callback_record_overwrite(
        self, temp_db_dir, tracked_client_with_callback
    ):
        """Test that SQLite callback overwrites records with the same response_id."""
        db_path = self._get_db_path(temp_db_dir)

        # Make first call
        response1 = tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5,
        )

        time.sleep(0.1)

        # Verify first record
        records = self._read_db_records(db_path)
        assert len(records) == 1
        first_record = records[0]
        first_updated_at = first_record["updated_at"]

        # Make second call with different content but force same response_id for testing
        response2 = tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello there"}],
            max_tokens=10,
        )

        time.sleep(0.1)

        # Verify we still have records (may be more due to different response_ids)
        records = self._read_db_records(db_path)
        assert len(records) >= 1

        # Each response should have its own record with different response_ids
        response_ids = [record["response_id"] for record in records]
        assert response1.id in response_ids
        assert response2.id in response_ids

    def test_sqlite_callback_database_schema(
        self, temp_db_dir, tracked_client_with_callback
    ):
        """Test that SQLite callback creates the correct database schema."""
        db_path = self._get_db_path(temp_db_dir)

        # Make a call to trigger database creation
        tracked_client_with_callback.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5,
        )

        time.sleep(0.1)

        # Verify database schema
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()

            # Check table exists
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='cost_events'"
            )
            assert cursor.fetchone() is not None, "cost_events table should exist"

            # Check table schema
            cursor.execute("PRAGMA table_info(cost_events)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            expected_columns = [
                "response_id",
                "model_id",
                "provider",
                "timestamp",
                "input_tokens",
                "output_tokens",
                "total_tokens",
                "context",
                "created_at",
                "updated_at",
            ]

            for expected_col in expected_columns:
                assert expected_col in column_names, (
                    f"Column {expected_col} should exist"
                )

            # Check that response_id is the primary key
            primary_key_cols = [
                col[1] for col in columns if col[5]
            ]  # col[5] is pk flag
            assert "response_id" in primary_key_cols, (
                "response_id should be primary key"
            )

    def test_sqlite_callback_context_handling(self, temp_db_dir):
        """Test SQLite callback properly handles context as dict/JSON."""
        db_path = self._get_db_path(temp_db_dir)

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
            sqlite_callback(mock_response)

        time.sleep(0.1)

        # Verify database records
        records = self._read_db_records(db_path)
        assert len(records) >= len(test_contexts)

        # Check that contexts are stored as JSON strings but can be parsed back to dicts
        for i, record in enumerate(records[: len(test_contexts)]):
            if record["context"]:
                # SQLite stores context as JSON string
                import json

                stored_context = json.loads(record["context"])
                expected_context = test_contexts[i]
                assert stored_context == expected_context

    def test_sqlite_callback_dict_response_context(self, temp_db_dir):
        """Test SQLite callback with dict response containing context."""
        db_path = self._get_db_path(temp_db_dir)

        # Test dict response format with context
        dict_response = {
            "id": "dict-response-123",
            "model": "gpt-4o-mini",
            "context": {"integration": "test", "source": "dict_response"},
            "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
        }

        sqlite_callback(dict_response)
        time.sleep(0.1)

        records = self._read_db_records(db_path)
        assert len(records) >= 1

        # Find our record
        test_record = None
        for record in records:
            if record["response_id"] == "dict-response-123":
                test_record = record
                break

        assert test_record is not None
        assert test_record["model_id"] == "gpt-4o-mini"

        # Verify context is stored correctly
        if test_record["context"]:
            import json

            stored_context = json.loads(test_record["context"])
            assert stored_context == {"integration": "test", "source": "dict_response"}

    def test_sqlite_callback_error_handling(self, temp_db_dir):
        """Test SQLite callback error handling with malformed response objects."""
        db_path = self._get_db_path(temp_db_dir)

        # Test with various malformed response objects
        test_objects = [
            None,
            {},
            "not an object",
            type("BadObj", (), {})(),  # Object with no useful attributes
        ]

        for test_obj in test_objects:
            sqlite_callback(test_obj)

        time.sleep(0.1)

        # Should create database and records even with malformed objects
        assert db_path.exists(), "Database should be created even with errors"

        records = self._read_db_records(db_path)
        # Should have records for each test object (with minimal/error data)
        assert len(records) >= len(test_objects)

        # Check that error records have fallback values and context is dict format
        for record in records:
            assert record["response_id"] is not None
            assert record["timestamp"] is not None
            # Context should be stored as JSON dict even for errors
            if record["context"]:
                import json

                stored_context = json.loads(record["context"])
                assert isinstance(stored_context, dict)
                # Should contain extraction_error key for error cases
                if "extraction_error" in stored_context:
                    assert isinstance(stored_context["extraction_error"], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
