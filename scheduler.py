"""
Scheduling and execution evaluation module.
Determines whether the current request matches the configured daily execution window,
handles duplicate prevention, concurrency locking, and execution tracking.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Tuple

from config import (
    APP_TIMEZONE,
    TIMEZONE_STR,
    SEND_HOUR,
    SEND_MINUTE,
    EXECUTION_WINDOW_MINUTES
)
from state_store import get_state_store, BaseStateStore
from gmail_service import send_all_drafts

logger = logging.getLogger("scheduler")


def get_current_localized_time() -> datetime:
    """Returns the current timezone-aware datetime object."""
    return datetime.now(APP_TIMEZONE)


def is_within_execution_window(
    now: datetime,
    target_hour: int = SEND_HOUR,
    target_minute: int = SEND_MINUTE,
    window_minutes: int = EXECUTION_WINDOW_MINUTES
) -> Tuple[bool, str]:
    """
    Checks whether the given localized datetime falls within the execution window.
    Window runs from [target_hour:target_minute] to [target_hour:target_minute + window_minutes].
    """
    current_minutes_of_day = now.hour * 60 + now.minute
    target_minutes_of_day = target_hour * 60 + target_minute

    # Calculate difference from target send time
    diff = current_minutes_of_day - target_minutes_of_day

    if 0 <= diff < window_minutes:
        return True, f"Within allowed window (+{diff}m from {target_hour:02d}:{target_minute:02d})"
    elif diff < 0:
        return False, f"Before scheduled time ({target_hour:02d}:{target_minute:02d} {TIMEZONE_STR})"
    else:
        return False, f"Outside scheduled window ({target_hour:02d}:{target_minute:02d} {TIMEZONE_STR})"


def evaluate_and_trigger(
    store: BaseStateStore = None,
    force: bool = False
) -> Dict[str, Any]:
    """
    Core execution logic triggered by every incoming uptime request.
    
    1. Evaluates current localized datetime.
    2. Verifies if current time is within daily execution window (or if forced).
    3. Checks persistent store to verify if already executed today.
    4. Acquires atomic lock to prevent concurrent double-sends.
    5. Executes send_all_drafts() if eligible.
    6. Records successful execution for today.
    """
    if store is None:
        store = get_state_store()

    now = get_current_localized_time()
    today_str = now.strftime("%Y-%m-%d")
    current_time_str = now.strftime("%H:%M:%S")

    # Step 1: Time Window Check
    in_window, window_reason = is_within_execution_window(now)

    if not in_window and not force:
        return {
            "status": "idle",
            "action": "skipped",
            "reason": window_reason,
            "current_time": f"{current_time_str} ({TIMEZONE_STR})",
            "scheduled_time": f"{SEND_HOUR:02d}:{SEND_MINUTE:02d} ({TIMEZONE_STR})",
            "date": today_str
        }

    # Step 2: Check if already sent today
    if store.has_run_today(today_str) and not force:
        logger.info("Daily send already completed for today (%s). Skipping.", today_str)
        return {
            "status": "idle",
            "action": "skipped",
            "reason": "already_executed_today",
            "message": f"Daily draft sending has already completed for {today_str}.",
            "current_time": f"{current_time_str} ({TIMEZONE_STR})",
            "date": today_str
        }

    # Step 3: Concurrency Lock Acquisition
    acquired, lock_token_or_reason = store.acquire_lock(today_str)
    if not acquired:
        logger.warning("Could not acquire execution lock for %s: %s", today_str, lock_token_or_reason)
        return {
            "status": "in_progress",
            "action": "skipped",
            "reason": "concurrency_lock_active",
            "message": lock_token_or_reason,
            "current_time": f"{current_time_str} ({TIMEZONE_STR})",
            "date": today_str
        }

    lock_token = lock_token_or_reason

    # Step 4: Execute draft sending
    logger.info("Executing daily draft send for date %s (force=%s)...", today_str, force)
    try:
        results = send_all_drafts()

        # Step 5: Record success
        store.record_success(today_str, results)

        return {
            "status": "success",
            "action": "executed",
            "date": today_str,
            "executed_at": current_time_str,
            "timezone": TIMEZONE_STR,
            "forced": force,
            "results": results
        }

    except Exception as e:
        logger.error("Error during scheduled draft execution: %s", e)
        return {
            "status": "error",
            "action": "failed",
            "date": today_str,
            "executed_at": current_time_str,
            "error": str(e)
        }

    finally:
        # Step 6: Always release lock
        store.release_lock(lock_token)
