"""
Unit tests for scheduler and time window evaluation.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import MagicMock, patch

from scheduler import is_within_execution_window, evaluate_and_trigger
from state_store import FileStateStore

TZ = ZoneInfo("Asia/Kolkata")


def test_time_before_scheduled():
    """Test 1: Current time is before scheduled time (e.g. 08:30 vs 09:00)."""
    current_time = datetime(2026, 9, 4, 8, 30, 0, tzinfo=TZ)
    in_window, reason = is_within_execution_window(current_time, target_hour=9, target_minute=0, window_minutes=5)
    assert in_window is False
    assert "Before scheduled time" in reason


def test_time_exactly_scheduled():
    """Test 2: Current time is exactly scheduled time (09:00 vs 09:00)."""
    current_time = datetime(2026, 9, 4, 9, 0, 0, tzinfo=TZ)
    in_window, reason = is_within_execution_window(current_time, target_hour=9, target_minute=0, window_minutes=5)
    assert in_window is True
    assert "Within allowed window" in reason


def test_time_after_scheduled_window():
    """Test 3: Current time is after scheduled window (09:10 vs 09:00 with 5m window)."""
    current_time = datetime(2026, 9, 4, 9, 10, 0, tzinfo=TZ)
    in_window, reason = is_within_execution_window(current_time, target_hour=9, target_minute=0, window_minutes=5)
    assert in_window is False
    assert "Outside scheduled window" in reason


def test_already_sent_today(tmp_path):
    """Test 4: Already sent today - should return idle without calling draft sender."""
    test_state_file = str(tmp_path / "test_state.json")
    store = FileStateStore(test_state_file)

    today_str = datetime.now(TZ).strftime("%Y-%m-%d")
    store.record_success(today_str, {"status": "completed", "sent": 5})

    with patch("scheduler.send_all_drafts") as mock_sender, \
         patch("scheduler.is_within_execution_window", return_value=(True, "In window")):
        result = evaluate_and_trigger(store=store, force=False)

        assert result["status"] == "idle"
        assert result["reason"] == "already_executed_today"
        mock_sender.assert_not_called()
