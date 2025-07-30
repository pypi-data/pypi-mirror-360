"""
Test thread safety and resource management of the usage tracker.
These tests simulate web server-like usage patterns to verify safety.
"""

import concurrent.futures
import time

import pytest

from llmcosts.tracker.usage_delivery import (
    create_usage_tracker,
    get_global_tracker_health,
    get_usage_tracker,
    reset_global_tracker,
)


@pytest.fixture(autouse=True)
def cleanup_tracker():
    """Clean up global tracker before and after each test."""
    reset_global_tracker()
    yield
    reset_global_tracker()


def test_concurrent_access():
    """Test concurrent access to the global tracker."""

    def worker(worker_id):
        tracker = get_usage_tracker()
        health_before = tracker.get_health_info()

        # Simulate tracking some usage
        tracker.track(
            {
                "model_id": "test-model",
                "response_id": f"worker-{worker_id}-{int(time.time())}",
                "input_tokens": 10,
                "output_tokens": 5,
            }
        )

        health_after = tracker.get_health_info()
        return {
            "worker_id": worker_id,
            "thread_name_before": health_before["worker_thread_name"],
            "thread_name_after": health_after["worker_thread_name"],
            "same_thread": health_before["worker_thread_name"]
            == health_after["worker_thread_name"],
        }

    # Run 10 concurrent workers
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        results = [
            future.result() for future in concurrent.futures.as_completed(futures)
        ]

    # Verify all workers used the same thread
    thread_names = [r["thread_name_after"] for r in results]
    unique_threads = set(thread_names)

    assert len(unique_threads) == 1, f"Expected 1 thread, got {len(unique_threads)}"
    assert len(results) == 10, "Should have 10 worker results"

    # Verify all workers completed successfully
    for result in results:
        assert "worker_id" in result
        assert "thread_name_before" in result
        assert "thread_name_after" in result


def test_restart_behavior():
    """Test tracker restart behavior."""
    # Get initial tracker
    tracker = get_usage_tracker()
    initial_health = tracker.get_health_info()
    initial_thread_name = initial_health["worker_thread_name"]

    assert initial_health["is_healthy"], "Initial tracker should be healthy"
    assert initial_health["worker_thread_alive"], (
        "Initial worker thread should be alive"
    )

    # Shutdown the tracker
    tracker.shutdown()
    time.sleep(0.5)  # Give it time to shutdown

    health_after_shutdown = tracker.get_health_info()
    assert health_after_shutdown["status"] == "stopped", (
        "Tracker should be stopped after shutdown"
    )
    assert health_after_shutdown["can_restart"], "Tracker should be able to restart"
    assert not health_after_shutdown["worker_thread_alive"], (
        "Worker thread should not be alive after shutdown"
    )

    # Try to use it again (should restart automatically)
    tracker.track(
        {
            "model_id": "test-model-restart",
            "response_id": f"restart-test-{int(time.time())}",
            "input_tokens": 15,
            "output_tokens": 8,
        }
    )

    time.sleep(0.5)  # Give it time to start

    health_after_restart = tracker.get_health_info()
    restarted_thread_name = health_after_restart["worker_thread_name"]

    assert health_after_restart["status"] == "running", (
        "Tracker should be running after restart"
    )
    assert health_after_restart["worker_thread_alive"], (
        "Worker thread should be alive after restart"
    )
    assert initial_thread_name != restarted_thread_name, (
        "Should create a new thread after restart"
    )


def test_memory_usage():
    """Test memory and resource usage."""
    # Create multiple tracker instances to verify resource limits
    trackers = []
    for i in range(5):
        tracker = create_usage_tracker(
            max_queue_size=10,  # Small queue for testing
        )
        trackers.append(tracker)

        # Add some data to each
        for j in range(15):  # More than queue size to test limits
            tracker.track(
                {
                    "model_id": f"test-model-{i}",
                    "response_id": f"mem-test-{i}-{j}-{int(time.time())}",
                    "input_tokens": j,
                    "output_tokens": j * 2,
                }
            )

    # Check resource usage
    total_threads = 0
    total_queue_size = 0

    for i, tracker in enumerate(trackers):
        health = tracker.get_health_info()
        if health["worker_thread_alive"]:
            total_threads += 1
        total_queue_size += health["queue_size"]

        # Queue should be at most 10 items (max_queue_size)
        assert health["queue_size"] <= 10, (
            f"Tracker {i} queue size {health['queue_size']} exceeds limit"
        )

        # Queue utilization should be reasonable
        assert health["queue_utilization"] <= 1.0, (
            f"Tracker {i} queue utilization exceeds 100%"
        )

        # Shutdown to cleanup
        tracker.shutdown()

    # Should have created at most 5 threads (one per tracker)
    assert total_threads <= 5, f"Too many threads created: {total_threads}"

    # Total queue size should be reasonable (each queue max 10 items)
    assert total_queue_size <= 50, f"Total queue size too large: {total_queue_size}"


def test_global_tracker_health_monitoring():
    """Test health monitoring features."""
    # Reset to start fresh
    reset_global_tracker()

    # Get health of non-existent tracker
    health = get_global_tracker_health()
    assert health is None, "Health should be None for non-existent tracker"

    # Create and use tracker
    tracker = get_usage_tracker()
    health = get_global_tracker_health()

    assert health is not None, "Health should not be None for existing tracker"
    assert health["status"] in ["running", "idle"], (
        f"Invalid status: {health['status']}"
    )
    assert health["is_healthy"], "Tracker should be healthy"
    assert 0.0 <= health["queue_utilization"] <= 1.0, (
        "Queue utilization should be between 0 and 1"
    )
    assert health["worker_thread_alive"], "Worker thread should be alive"
    assert "total_sent" in health, "Health should include total_sent"
    assert "total_failed" in health, "Health should include total_failed"
    assert "consecutive_permanent_failures" in health, (
        "Health should include consecutive_permanent_failures"
    )


def test_thread_safety_edge_cases():
    """Test edge cases for thread safety."""
    # Test rapid start/stop cycles
    tracker = get_usage_tracker()

    for i in range(5):
        # Track some data
        tracker.track(
            {
                "model_id": f"edge-test-{i}",
                "response_id": f"edge-{i}-{int(time.time())}",
                "input_tokens": 1,
                "output_tokens": 1,
            }
        )

        # Shutdown and restart
        tracker.shutdown()
        time.sleep(0.1)

        # Should be able to restart
        health = tracker.get_health_info()
        assert health["can_restart"], f"Should be able to restart after cycle {i}"

        # Track more data (should auto-restart)
        tracker.track(
            {
                "model_id": f"edge-restart-{i}",
                "response_id": f"edge-restart-{i}-{int(time.time())}",
                "input_tokens": 2,
                "output_tokens": 2,
            }
        )

        time.sleep(0.1)

        # Should be running again
        health = tracker.get_health_info()
        assert health["status"] == "running", (
            f"Should be running after restart cycle {i}"
        )
