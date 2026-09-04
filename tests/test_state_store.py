"""
Unit tests for StateStore (Redis and File-based locking and duplicate detection).
"""

from unittest.mock import MagicMock, patch
from state_store import RedisStateStore, FileStateStore


def test_file_state_store_lock_and_run(tmp_path):
    """Verify FileStateStore correctly handles locking, execution tracking, and releasing."""
    state_file = str(tmp_path / "test_store.json")
    store = FileStateStore(filepath=state_file)

    date_str = "2026-09-04"

    # Initially hasn't run
    assert store.has_run_today(date_str) is False

    # Acquire lock
    acquired, token = store.acquire_lock(date_str)
    assert acquired is True
    assert token is not None

    # Record success
    store.record_success(date_str, {"sent": 3, "failed": 0})
    store.release_lock(token)

    # Now has_run_today is True
    assert store.has_run_today(date_str) is True

    # Next lock acquisition attempt should be rejected
    acquired_again, reason = store.acquire_lock(date_str)
    assert acquired_again is False
    assert "already completed" in reason


def test_redis_state_store_locking():
    """Verify RedisStateStore distributed locking and state retrieval."""
    mock_redis = MagicMock()
    
    # Simulate fresh state
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    with patch("redis.from_url", return_value=mock_redis):
        store = RedisStateStore("redis://localhost:6379")

        # Check has_run_today
        assert store.has_run_today("2026-09-04") is False

        # Acquire lock
        acquired, token = store.acquire_lock("2026-09-04")
        assert acquired is True
        mock_redis.set.assert_called_with(
            "draftblaster:lock", token, nx=True, ex=300
        )

        # Release lock calls eval
        store.release_lock(token)
        mock_redis.eval.assert_called_once()
