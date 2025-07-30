"""
Response callback functions for LLM cost tracking.

This package provides example callback functions that can be used with LLMTrackingProxy
to record response data as it comes in from LLM API calls.

Available callbacks:
- sqlite_callback: Records data to a SQLite database
- text_callback: Records data to a text file

Example usage:
    from tracker.callbacks import sqlite_callback
    from tracker import LLMTrackingProxy

    proxy = LLMTrackingProxy(client, provider=Provider.OPENAI, response_callback=sqlite_callback)
"""

from .sqlite_callback import sqlite_callback
from .text_callback import text_callback

__all__ = ["sqlite_callback", "text_callback"]
