"""
SQLite callback for recording LLM response cost data.

This callback extracts cost event summary data from LLM responses and stores it
in a SQLite database. The database and table are created automatically if they
don't exist.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from environs import Env

# Load environment variables
env = Env()


def _get_sqlite_path() -> str:
    """Get the SQLite database path from environment variables."""
    sqlite_path = env.str("SQLITE_CALLBACK_TARGET_PATH", None)
    if sqlite_path is None:
        raise ValueError(
            "SQLITE_CALLBACK_TARGET_PATH environment variable is required. "
            "Please set it to the directory where you want the SQLite database to be created."
        )
    return sqlite_path


def _normalize_model_id(model_id: str) -> str:
    """
    Normalize model IDs by removing version suffixes that aren't recognized by the server.

    Examples:
    - gpt-4o-mini-2024-07-18 -> gpt-4o-mini
    - gpt-4o-2024-05-13 -> gpt-4o
    - gpt-3.5-turbo-0125 -> gpt-3.5-turbo-0125 (keep this one as server recognizes it)
    """
    if not model_id:
        return model_id

    # Remove common version suffixes for gpt-4o family models
    if model_id.startswith("gpt-4o-mini-"):
        return "gpt-4o-mini"
    elif model_id.startswith("gpt-4o-") and "-20" in model_id:
        return "gpt-4o"
    elif model_id.startswith("gpt-4-turbo-") and "-20" in model_id:
        return "gpt-4-turbo"

    # Keep other model IDs as-is
    return model_id


def _extract_cost_event_data(response: Any) -> Optional[Dict[str, Any]]:
    """Extract cost event data from an LLM response object."""
    try:
        # Initialize the cost event data
        cost_data = {
            "response_id": None,
            "model_id": None,
            "provider": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "context": None,  # Should be a dict/JSON when present
        }

        # Extract response_id
        if hasattr(response, "id"):
            cost_data["response_id"] = response.id
        elif hasattr(response, "response") and hasattr(response.response, "id"):
            cost_data["response_id"] = response.response.id
        elif isinstance(response, dict):
            cost_data["response_id"] = (
                response.get("id")
                or response.get("request_id")
                or response.get("ResponseMetadata", {}).get("RequestId")
            )

        # Generate UUID if no response_id found
        if not cost_data["response_id"]:
            cost_data["response_id"] = str(uuid.uuid4())

        # Extract model_id and normalize it
        raw_model = None
        if hasattr(response, "model"):
            raw_model = response.model
        elif hasattr(response, "response") and hasattr(response.response, "model"):
            raw_model = response.response.model
        elif isinstance(response, dict) and "model" in response:
            raw_model = response["model"]

        if raw_model:
            cost_data["model_id"] = _normalize_model_id(raw_model)

        # Infer provider from response characteristics
        provider = None
        response_str = str(type(response)).lower()
        if "openai" in response_str:
            provider = "openai"
        elif "anthropic" in response_str:
            provider = "anthropic"
        elif "google" in response_str or "gemini" in response_str:
            provider = "google"
        elif hasattr(response, "ResponseMetadata"):
            provider = "amazon-bedrock"  # AWS Bedrock pattern

        cost_data["provider"] = provider

        # Extract context if available (should be a dict/JSON)
        if hasattr(response, "context") and isinstance(response.context, dict):
            cost_data["context"] = response.context
        elif (
            isinstance(response, dict)
            and "context" in response
            and isinstance(response["context"], dict)
        ):
            cost_data["context"] = response["context"]

        # Extract usage/token information
        usage = None
        if hasattr(response, "usage"):
            usage = response.usage
        elif hasattr(response, "response") and hasattr(response.response, "usage"):
            usage = response.response.usage
        elif isinstance(response, dict) and "usage" in response:
            usage = response["usage"]

        if usage:
            # Handle different usage formats
            if hasattr(usage, "prompt_tokens"):
                cost_data["input_tokens"] = usage.prompt_tokens
            elif hasattr(usage, "input_tokens"):
                cost_data["input_tokens"] = usage.input_tokens
            elif isinstance(usage, dict):
                cost_data["input_tokens"] = usage.get("prompt_tokens") or usage.get(
                    "input_tokens"
                )

            if hasattr(usage, "completion_tokens"):
                cost_data["output_tokens"] = usage.completion_tokens
            elif hasattr(usage, "output_tokens"):
                cost_data["output_tokens"] = usage.output_tokens
            elif isinstance(usage, dict):
                cost_data["output_tokens"] = usage.get(
                    "completion_tokens"
                ) or usage.get("output_tokens")

            if hasattr(usage, "total_tokens"):
                cost_data["total_tokens"] = usage.total_tokens
            elif isinstance(usage, dict) and "total_tokens" in usage:
                cost_data["total_tokens"] = usage["total_tokens"]
            elif cost_data["input_tokens"] and cost_data["output_tokens"]:
                cost_data["total_tokens"] = (
                    cost_data["input_tokens"] + cost_data["output_tokens"]
                )

        return cost_data

    except Exception as e:
        # Return minimal data if extraction fails
        return {
            "response_id": str(uuid.uuid4()),
            "model_id": "unknown",
            "provider": "unknown",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_tokens": None,
            "output_tokens": None,
            "total_tokens": None,
            "context": {"extraction_error": str(e)},  # Keep as dict for consistency
        }


def _ensure_database_and_table(db_path: str) -> None:
    """Ensure the database and cost_events table exist."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_events (
                response_id TEXT PRIMARY KEY,
                model_id TEXT,
                provider TEXT,
                timestamp TEXT,
                input_tokens INTEGER,
                output_tokens INTEGER,
                total_tokens INTEGER,
                context TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()


def sqlite_callback(response: Any) -> None:
    """
    Callback function that records LLM response cost data to a SQLite database.

    This function extracts cost event summary data from the response and stores it
    in a SQLite database. If a record with the same response_id already exists,
    it will be overwritten.

    Args:
        response: The LLM response object from any provider

    Raises:
        ValueError: If SQLITE_CALLBACK_TARGET_PATH environment variable is not set

    Environment Variables:
        SQLITE_CALLBACK_TARGET_PATH: Directory path where the SQLite database will be created
    """
    try:
        # Get database path
        target_dir = _get_sqlite_path()
        db_path = Path(target_dir) / "llm_cost_events.db"

        # Ensure directory exists
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Ensure database and table exist
        _ensure_database_and_table(str(db_path))

        # Extract cost event data
        cost_data = _extract_cost_event_data(response)
        if not cost_data:
            return

        # Prepare data for database insertion
        current_time = datetime.now(timezone.utc).isoformat()

        # Convert context to JSON string if it's not already a string
        context = cost_data.get("context")
        if context and not isinstance(context, str):
            context = json.dumps(context)

        # Insert or replace the record
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO cost_events (
                    response_id, model_id, provider, timestamp,
                    input_tokens, output_tokens, total_tokens, context,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 
                         COALESCE((SELECT created_at FROM cost_events WHERE response_id = ?), ?),
                         ?)
            """,
                (
                    cost_data["response_id"],
                    cost_data["model_id"],
                    cost_data["provider"],
                    cost_data["timestamp"],
                    cost_data["input_tokens"],
                    cost_data["output_tokens"],
                    cost_data["total_tokens"],
                    context,
                    cost_data["response_id"],  # For COALESCE lookup
                    current_time,  # created_at if new record
                    current_time,  # updated_at always current time
                ),
            )
            conn.commit()

    except Exception as e:
        # Log error but don't raise to avoid breaking the main flow
        import logging

        logging.error(f"Error in sqlite_callback: {e}")
