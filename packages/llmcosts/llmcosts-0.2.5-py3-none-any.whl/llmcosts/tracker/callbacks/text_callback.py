"""
Text file callback for recording LLM response cost data.

This callback extracts cost event summary data from LLM responses and stores it
in a text file in JSON format. Each record is stored as a JSON line, and records
with the same response_id are overwritten.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from environs import Env

# Load environment variables
env = Env()


def _get_text_path() -> str:
    """Get the text file path from environment variables."""
    text_path = env.str("TEXT_CALLBACK_TARGET_PATH", None)
    if text_path is None:
        raise ValueError(
            "TEXT_CALLBACK_TARGET_PATH environment variable is required. "
            "Please set it to the directory where you want the text file to be created."
        )
    return text_path


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


def _read_existing_records(file_path: Path) -> Dict[str, Dict[str, Any]]:
    """Read existing records from the text file."""
    records = {}
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            record = json.loads(line)
                            if "response_id" in record:
                                records[record["response_id"]] = record
                        except json.JSONDecodeError as e:
                            # Skip malformed lines but continue processing
                            import logging

                            logging.warning(
                                f"Skipping malformed JSON on line {line_num}: {e}"
                            )
                            continue
        except Exception as e:
            # If we can't read the file, start fresh
            import logging

            logging.warning(f"Could not read existing records: {e}")

    return records


def _write_records(file_path: Path, records: Dict[str, Dict[str, Any]]) -> None:
    """Write all records to the text file."""
    with open(file_path, "w", encoding="utf-8") as f:
        for record in records.values():
            f.write(json.dumps(record, separators=(",", ":")) + "\n")


def text_callback(response: Any) -> None:
    """
    Callback function that records LLM response cost data to a text file.

    This function extracts cost event summary data from the response and stores it
    in a text file in JSON Lines format. Each record is a JSON object on its own line.
    If a record with the same response_id already exists, it will be overwritten.

    Args:
        response: The LLM response object from any provider

    Raises:
        ValueError: If TEXT_CALLBACK_TARGET_PATH environment variable is not set

    Environment Variables:
        TEXT_CALLBACK_TARGET_PATH: Directory path where the text file will be created
    """
    try:
        # Get file path
        target_dir = _get_text_path()
        file_path = Path(target_dir) / "llm_cost_events.jsonl"

        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract cost event data
        cost_data = _extract_cost_event_data(response)
        if not cost_data:
            return

        # Add metadata
        current_time = datetime.now(timezone.utc).isoformat()
        cost_data["updated_at"] = current_time

        # Read existing records
        existing_records = _read_existing_records(file_path)

        # Check if this is an update or new record
        response_id = cost_data["response_id"]
        if response_id in existing_records:
            # Preserve created_at for existing records
            cost_data["created_at"] = existing_records[response_id].get(
                "created_at", current_time
            )
        else:
            # New record
            cost_data["created_at"] = current_time

        # Update the records
        existing_records[response_id] = cost_data

        # Write all records back to file
        _write_records(file_path, existing_records)

    except Exception as e:
        # Log error but don't raise to avoid breaking the main flow
        import logging

        logging.error(f"Error in text_callback: {e}")
