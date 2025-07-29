import atexit
import logging
import os
import queue
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional

# We use the synchronous ``requests`` library for delivery. It offers a
# straightforward retry mechanism via ``HTTPAdapter`` and works well in our
# background thread. ``httpx`` is great for async or HTTP/2 use cases, but here
# it would add complexity without much benefit.
import requests
from requests.adapters import HTTPAdapter, Retry

from ..client import LLMCostsClient

DEFAULT_API_ENDPOINT = "https://llmcosts.com/api/v1/usage"


class TrackerStatus(Enum):
    """Status of the usage tracker."""

    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"


class UsageTracker:
    """Threaded usage delivery worker with robust error handling.

    Parameters
    ----------
    api_endpoint:
        Endpoint for sending usage data.
    api_key:
        API key for authentication.
    batch_size:
        Number of records to send per request.
    max_retries:
        How many times to retry on network errors.
    backoff_factor:
        Exponential backoff factor between retries.
    timeout:
        Request timeout in seconds.
    fail_fast:
        Stop after first permanent error.
    max_queue_size:
        Maximum queued records before dropping new ones.
    sync_mode:
        If ``True``, deliver records synchronously in the caller's thread.
    client:
        Optional :class:`LLMCostsClient` instance to reuse.
    """

    def __init__(
        self,
        api_endpoint: str = DEFAULT_API_ENDPOINT,
        api_key: Optional[str] = None,
        batch_size: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        timeout: int = 10,
        fail_fast: bool = False,
        max_queue_size: int = 1000,  # Add queue size limit
        sync_mode: bool = False,  # New: synchronous mode for immediate responses
        client: Optional[LLMCostsClient] = None,
    ) -> None:
        if not api_endpoint:
            raise ValueError("API endpoint is required")

        self.api_endpoint = api_endpoint
        self.api_key = api_key or os.environ.get("LLMCOSTS_API_KEY", "")
        self.batch_size = batch_size
        self.fail_fast = fail_fast
        self.max_queue_size = max_queue_size
        self.sync_mode = sync_mode

        # Reuse a provided LLMCostsClient or create one based on the endpoint
        self.client = client
        if self.client is None:
            base_url = api_endpoint.rsplit("/", 1)[0]
            self.client = LLMCostsClient(api_key=self.api_key, base_url=base_url)

        # Add maxsize to prevent unbounded memory growth
        self._queue: queue.Queue[Dict[str, Any]] = queue.Queue(maxsize=max_queue_size)
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._start_lock = threading.Lock()  # Prevent race conditions in start()

        # Status tracking
        self._status = TrackerStatus.IDLE
        self._last_error: Optional[str] = None
        self._consecutive_permanent_failures = 0
        self._max_consecutive_failures = 3

        # Statistics
        self._total_sent = 0
        self._total_failed = 0

        # Last response for sync mode
        self._last_response: Optional[Dict[str, Any]] = None
        self._last_response_lock = threading.Lock()

        self._session = self.client.session
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],  # Only retry server errors
        )
        self._session.mount("https://", HTTPAdapter(max_retries=retries))
        self._session.mount("http://", HTTPAdapter(max_retries=retries))
        self.timeout = timeout

        atexit.register(self.shutdown)

    @property
    def status(self) -> TrackerStatus:
        """Get the current status of the tracker."""
        return self._status

    @property
    def last_error(self) -> Optional[str]:
        """Get the last error that occurred."""
        return self._last_error

    @property
    def stats(self) -> Dict[str, int]:
        """Get tracker statistics."""
        return {
            "total_sent": self._total_sent,
            "total_failed": self._total_failed,
            "queue_size": self._queue.qsize(),
            "queue_max_size": self.max_queue_size,
        }

    def start(self) -> None:
        """Start the worker thread safely, handling race conditions and restarts."""
        with self._start_lock:
            # Double-check pattern: check again inside the lock
            if self._worker_thread.is_alive():
                return  # Already running

            # If the thread has been started before, we need to create a new one
            # because threads can only be started once
            if (
                hasattr(self._worker_thread, "_started")
                and self._worker_thread._started.is_set()
            ):
                # Reset stop event for new thread
                self._stop_event.clear()
                # Create new thread object
                self._worker_thread = threading.Thread(target=self._worker, daemon=True)

            self._status = TrackerStatus.RUNNING
            self._worker_thread.start()

    def track(self, usage_data: Dict[str, Any]) -> None:
        if self._status == TrackerStatus.FAILED and self.fail_fast:
            logging.warning("Tracker is in failed state. Dropping usage data.")
            return

        if not self.sync_mode and not self._worker_thread.is_alive():
            self.start()

        if self.sync_mode:
            # In sync mode, send immediately and return response
            self._send_sync(usage_data)
        else:
            # In batch mode, queue for later processing
            try:
                self._queue.put_nowait(usage_data)
            except queue.Full:
                logging.warning("Usage queue is full. Dropping usage data.")

    def _send_sync(self, usage_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send usage data synchronously and return server response."""
        try:
            # Determine remote_save flag from usage data
            remote_save = usage_data.get("remote_save", True)

            # Remove remote_save from usage data if present (it's a top-level flag)
            usage_data_clean = usage_data.copy()
            if "remote_save" in usage_data_clean:
                del usage_data_clean["remote_save"]

            # Format request according to OpenAPI spec
            request_payload = {
                "usage_records": [usage_data_clean],
                "remote_save": remote_save,
            }

            res = self._session.post(
                self.api_endpoint, json=request_payload, timeout=self.timeout
            )

            # Handle success status codes based on new API spec
            # 200: All records processed successfully
            # 207: Partial success (some records failed) - this is still considered success
            if res.status_code in [200, 207]:
                response_data = res.json()

                # Store the response
                with self._last_response_lock:
                    self._last_response = response_data

                # Handle triggered thresholds from response
                self.client._handle_triggered_thresholds_in_response(response_data)

                # Update stats based on actual processed count from response
                processed_count = response_data.get("processed", 1)
                failed_count = response_data.get("failed", 0) or 0

                self._total_sent += processed_count
                if failed_count > 0:
                    self._total_failed += failed_count

                self._consecutive_permanent_failures = 0  # Reset on success
                return response_data
            else:
                # For non-success status codes, raise an HTTPError
                res.raise_for_status()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 0
            error_msg = f"HTTP error {status_code}: {e}"
            logging.error(f"Failed to deliver usage data synchronously - {error_msg}")
            self._last_error = error_msg
            self._total_failed += 1
            return None

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            logging.error(f"Failed to deliver usage data synchronously - {error_msg}")
            self._last_error = error_msg
            self._total_failed += 1
            return None

    def get_last_response(self) -> Optional[Dict[str, Any]]:
        """Get the last server response (for sync mode)."""
        with self._last_response_lock:
            return self._last_response.copy() if self._last_response else None

    def clear_stored_responses(self) -> None:
        """Clear stored responses."""
        with self._last_response_lock:
            self._last_response = None

    def _is_permanent_error(self, status_code: int) -> bool:
        """Check if the HTTP status code represents a permanent error."""
        # Permanent errors that shouldn't be retried based on new API spec
        # 400: All records failed (bad request data)
        # 401: Unauthorized (bad API key)
        # 422: Unprocessable Entity (validation errors)
        return status_code in [400, 401, 422]

    def _is_rate_limit_error(self, status_code: int) -> bool:
        """Check if the HTTP status code represents rate limiting."""
        return status_code == 429

    def _send_batch(self, batch: List[Dict[str, Any]]) -> bool:
        """Send a batch of usage data. Returns True if successful."""
        if not batch:
            return True

        try:
            # Determine remote_save flag from batch
            # If any record has remote_save=False, set the top-level flag to False
            remote_save = True
            for record in batch:
                if record.get("remote_save", True) is False:
                    remote_save = False
                    break

            # Remove remote_save from individual records (it's a top-level flag)
            clean_batch = []
            for record in batch:
                clean_record = record.copy()
                if "remote_save" in clean_record:
                    del clean_record["remote_save"]
                clean_batch.append(clean_record)

            # Format request according to OpenAPI spec
            request_payload = {
                "usage_records": clean_batch,
                "remote_save": remote_save,
            }

            res = self._session.post(
                self.api_endpoint, json=request_payload, timeout=self.timeout
            )

            # Handle success status codes based on new API spec
            # 200: All records processed successfully
            # 207: Partial success (some records failed) - this is still considered success
            if res.status_code in [200, 207]:
                response_data = res.json()

                # Handle triggered thresholds from response
                self.client._handle_triggered_thresholds_in_response(response_data)

                # Update stats based on actual processed count from response
                processed_count = response_data.get("processed", len(batch))
                failed_count = response_data.get("failed", 0) or 0

                self._total_sent += processed_count
                if failed_count > 0:
                    self._total_failed += failed_count

                self._consecutive_permanent_failures = 0  # Reset on success
                return True
            else:
                # For non-success status codes, raise an HTTPError
                res.raise_for_status()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else 0

            if self._is_permanent_error(status_code):
                error_msg = f"Permanent error {status_code}: {e}"
                logging.error(f"Failed to deliver usage batch - {error_msg}")
                self._last_error = error_msg
                self._consecutive_permanent_failures += 1
                self._total_failed += len(batch)

                # In fail_fast mode, stop immediately on first permanent error
                # Otherwise, stop after too many consecutive permanent failures
                should_stop = (
                    self.fail_fast
                    or self._consecutive_permanent_failures
                    >= self._max_consecutive_failures
                )

                if should_stop:
                    self._status = TrackerStatus.FAILED
                    if self.fail_fast:
                        logging.error(
                            f"Stopping usage tracker immediately due to fail_fast mode. "
                            f"Permanent error: {error_msg}"
                        )
                    else:
                        logging.error(
                            f"Stopping usage tracker after {self._consecutive_permanent_failures} "
                            f"consecutive permanent failures. Last error: {error_msg}"
                        )
                    self._stop_event.set()

                return False

            elif self._is_rate_limit_error(status_code):
                error_msg = f"Rate limit error {status_code}: {e}"
                logging.warning(f"Rate limited - {error_msg}")
                self._last_error = error_msg
                # Rate limits are temporary, don't increment permanent failure count
                # The request library's retry logic will handle this
                return False

            else:
                # Temporary server errors - let the retry logic handle it
                error_msg = f"Temporary error {status_code}: {e}"
                logging.warning(f"Temporary error - {error_msg}")
                self._last_error = error_msg
                return False

        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {e}"
            logging.warning(f"Network error during batch delivery - {error_msg}")
            self._last_error = error_msg
            return False

    def _worker(self) -> None:
        """Worker thread that processes the queue."""
        while not self._stop_event.is_set():
            try:
                batch = [self._queue.get(timeout=1)]
                while len(batch) < self.batch_size:
                    try:
                        batch.append(self._queue.get_nowait())
                    except queue.Empty:
                        break

                success = self._send_batch(batch)

                # Mark tasks as done regardless of success
                # (failed items are logged/counted but not retried)
                for _ in batch:
                    self._queue.task_done()

                # In fail_fast mode, stop on first permanent error
                if (
                    not success
                    and self.fail_fast
                    and self._status == TrackerStatus.FAILED
                ):
                    break

            except queue.Empty:
                continue

        # Process remaining items in shutdown
        while not self._queue.empty():
            batch = []
            while len(batch) < self.batch_size and not self._queue.empty():
                batch.append(self._queue.get())
            if batch:
                self._send_batch(batch)
                for _ in batch:
                    self._queue.task_done()

        # Only set to STOPPED if not already FAILED
        if self._status != TrackerStatus.FAILED:
            self._status = TrackerStatus.STOPPED

    def shutdown(self) -> None:
        """Shutdown the tracker and wait for pending operations."""
        with self._start_lock:
            self._stop_event.set()

            # Wait for worker thread to finish first
            if self._worker_thread.is_alive():
                self._worker_thread.join(
                    timeout=10.0  # Give it 10 seconds to finish gracefully
                )

                # If thread is still alive after timeout, log warning
                if self._worker_thread.is_alive():
                    logging.warning(
                        "Worker thread did not shutdown gracefully within 10 seconds"
                    )

            # If there are still unprocessed items in the queue (e.g., worker exited early),
            # we need to mark them as done to prevent hanging in queue.join()
            unprocessed_count = 0
            while not self._queue.empty():
                try:
                    self._queue.get_nowait()
                    self._queue.task_done()
                    unprocessed_count += 1
                except queue.Empty:
                    break

            if unprocessed_count > 0:
                logging.warning(
                    f"Marked {unprocessed_count} unprocessed items as done during shutdown"
                )

            # Now join should not hang, but add a timeout just in case
            try:
                self._queue.join()
            except Exception as e:
                logging.warning(f"Error during queue join in shutdown: {e}")
                # Don't let shutdown errors cause hanging

            # Only update status to STOPPED if not already FAILED
            if self._status != TrackerStatus.FAILED:
                self._status = TrackerStatus.STOPPED

    def wait_for_delivery(self, timeout: float = 10.0) -> bool:
        """Wait for all queued items to be delivered or fail.

        Returns True if all items were processed, False if timeout occurred.
        Useful for tests that need to wait for delivery completion.
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self._queue.empty():
                return True
            if self._status == TrackerStatus.FAILED:
                return True  # Failed but processed
            # Also check if worker thread has died (e.g., due to fail_fast)
            if not self._worker_thread.is_alive() and self._status in [
                TrackerStatus.FAILED,
                TrackerStatus.STOPPED,
            ]:
                return True
            time.sleep(0.1)
        return False

    def is_healthy(self) -> bool:
        """Check if the tracker is in a healthy state."""
        return (
            self._status in [TrackerStatus.RUNNING, TrackerStatus.IDLE]
            and self._worker_thread.is_alive()
            and self._queue.qsize() < self.max_queue_size * 0.9  # Not nearly full
        )

    def can_restart(self) -> bool:
        """Check if the tracker can be safely restarted."""
        return (
            self._status in [TrackerStatus.STOPPED, TrackerStatus.FAILED]
            and not self._worker_thread.is_alive()
        )

    def get_health_info(self) -> Dict[str, Any]:
        """Get detailed health information about the tracker."""
        return {
            "status": self._status.value,
            "is_healthy": self.is_healthy(),
            "can_restart": self.can_restart(),
            "worker_thread_alive": self._worker_thread.is_alive(),
            "worker_thread_name": self._worker_thread.name,
            "queue_size": self._queue.qsize(),
            "queue_utilization": self._queue.qsize() / self.max_queue_size,
            "total_sent": self._total_sent,
            "total_failed": self._total_failed,
            "last_error": self._last_error,
            "consecutive_permanent_failures": self._consecutive_permanent_failures,
            "sync_mode": self.sync_mode,
        }


_tracker: Optional[UsageTracker] = None
_tracker_lock = threading.Lock()


def get_usage_tracker() -> UsageTracker:
    """Get the global usage tracker, creating it if necessary.

    ⚠️ **Advanced Use Only**: Most users should use `LLMTrackingProxy` which automatically
    handles tracker creation and management. Only use this function for debugging,
    health monitoring, or advanced integrations.

    This function is thread-safe and will restart a failed tracker if needed.

    Returns:
        UsageTracker: The global tracker instance.
    """
    global _tracker
    with _tracker_lock:
        if _tracker is None:
            endpoint = os.environ.get("LLMCOSTS_API_ENDPOINT", DEFAULT_API_ENDPOINT)
            key = os.environ.get("LLMCOSTS_API_KEY", "")
            _tracker = UsageTracker(api_endpoint=endpoint, api_key=key)
            _tracker.start()
        elif not _tracker.is_healthy() and _tracker.can_restart():
            # Tracker is unhealthy but can be restarted
            logging.info("Restarting unhealthy global usage tracker")
            try:
                _tracker.start()
            except Exception as e:
                logging.error(f"Failed to restart global usage tracker: {e}")
                # Don't replace the tracker, let it stay in failed state
        return _tracker


def set_global_usage_tracker(tracker: UsageTracker) -> None:
    """Set the global usage tracker instance.

    This is primarily for testing purposes.
    """
    global _tracker
    with _tracker_lock:
        _tracker = tracker


def reset_global_tracker() -> None:
    """Reset the global tracker. Useful for testing or error recovery."""
    global _tracker
    with _tracker_lock:
        if _tracker is not None:
            try:
                _tracker.shutdown()
            except Exception as e:
                logging.warning(f"Error shutting down global tracker during reset: {e}")
        _tracker = None


def get_global_tracker_health() -> Optional[Dict[str, Any]]:
    """Get health info for the global tracker, if it exists."""
    global _tracker
    with _tracker_lock:
        return _tracker.get_health_info() if _tracker is not None else None


def create_usage_tracker(
    api_key: Optional[str] = None,
    api_endpoint: Optional[str] = None,
    sync_mode: bool = False,
    client: Optional[LLMCostsClient] = None,
    **kwargs,
) -> UsageTracker:
    """Create a new UsageTracker instance with custom settings.

    Args:
        api_key: API key for llmcosts.com. If None, will look in environment.
        api_endpoint: API endpoint. If None, will use default or environment.
        sync_mode: If True, sends data immediately and returns responses.
        client: Optional pre-configured ``LLMCostsClient`` instance to use.
        **kwargs: Additional arguments passed to ``UsageTracker`` constructor.

    Returns:
        Configured UsageTracker instance.
    """
    endpoint = api_endpoint or os.environ.get(
        "LLMCOSTS_API_ENDPOINT", DEFAULT_API_ENDPOINT
    )
    key = api_key or os.environ.get("LLMCOSTS_API_KEY", "")

    tracker = UsageTracker(
        api_endpoint=endpoint,
        api_key=key,
        sync_mode=sync_mode,
        client=client,
        **kwargs,
    )

    # Start the tracker if not in sync mode
    if not sync_mode:
        tracker.start()

    return tracker
