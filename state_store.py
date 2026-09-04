"""
State store module for duplicate prevention and concurrency control.
Supports Redis (recommended for production on Render) and local file/disk fallback.
"""

import os
import json
import time
import uuid
import logging
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any

try:
    import fcntl
except ImportError:
    fcntl = None  # Windows compatibility fallback if needed

import redis

logger = logging.getLogger("state_store")


class BaseStateStore(ABC):
    """Abstract base class for state storage and distributed locking."""

    @abstractmethod
    def has_run_today(self, date_str: str) -> bool:
        """Check if sending was already completed for the given date (YYYY-MM-DD)."""
        pass

    @abstractmethod
    def acquire_lock(self, date_str: str) -> Tuple[bool, str]:
        """
        Attempt to acquire an exclusive lock to perform the daily send.
        Returns: (success: bool, reason_or_token: str)
        """
        pass

    @abstractmethod
    def release_lock(self, token: str) -> None:
        """Release the acquired lock."""
        pass

    @abstractmethod
    def record_success(self, date_str: str, summary: Dict[str, Any]) -> None:
        """Record that sending completed successfully for the given date."""
        pass

    @abstractmethod
    def get_last_run_info(self) -> Dict[str, Any]:
        """Retrieve details about the last recorded run."""
        pass


class RedisStateStore(BaseStateStore):
    """
    Redis-backed state store.
    Provides atomic distributed locking (SETNX with TTL) and persistent state across
    Render restarts and deploys. Recommended with free Upstash Redis.
    """

    LOCK_KEY = "draftblaster:lock"
    LAST_DATE_KEY = "draftblaster:last_send_date"
    LAST_SUMMARY_KEY = "draftblaster:last_summary"
    LOCK_TIMEOUT_SECONDS = 300  # 5 minutes max lock duration

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = redis.from_url(redis_url, decode_responses=True)
        logger.info("Initialized RedisStateStore with Redis connection.")

    def has_run_today(self, date_str: str) -> bool:
        try:
            last_date = self.client.get(self.LAST_DATE_KEY)
            return last_date == date_str
        except Exception as e:
            logger.error("Redis error checking has_run_today: %s", e)
            return False

    def acquire_lock(self, date_str: str) -> Tuple[bool, str]:
        # Pre-check before acquiring lock
        if self.has_run_today(date_str):
            return False, f"Sending was already completed for today ({date_str})."

        token = str(uuid.uuid4())
        try:
            # Atomic distributed lock: set only if not exists (NX) with expiration (EX)
            acquired = self.client.set(self.LOCK_KEY, token, nx=True, ex=self.LOCK_TIMEOUT_SECONDS)
            if not acquired:
                return False, "Another process or concurrent request is currently sending drafts."

            # Double-check date after acquiring lock to prevent race conditions
            if self.has_run_today(date_str):
                self.release_lock(token)
                return False, f"Sending was already completed for today ({date_str})."

            return True, token
        except Exception as e:
            logger.error("Redis error acquiring lock: %s", e)
            return False, f"Redis error during lock acquisition: {e}"

    def release_lock(self, token: str) -> None:
        # Atomic release using Lua script so we only delete our own lock token
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            self.client.eval(lua_script, 1, self.LOCK_KEY, token)
        except Exception as e:
            logger.error("Redis error releasing lock: %s", e)

    def record_success(self, date_str: str, summary: Dict[str, Any]) -> None:
        try:
            pipe = self.client.pipeline()
            # Retain date for 7 days
            pipe.set(self.LAST_DATE_KEY, date_str, ex=7 * 86400)
            pipe.set(self.LAST_SUMMARY_KEY, json.dumps(summary), ex=7 * 86400)
            pipe.execute()
            logger.info("Recorded successful daily send in Redis for date %s", date_str)
        except Exception as e:
            logger.error("Redis error recording success: %s", e)

    def get_last_run_info(self) -> Dict[str, Any]:
        try:
            last_date = self.client.get(self.LAST_DATE_KEY)
            summary_raw = self.client.get(self.LAST_SUMMARY_KEY)
            summary = json.loads(summary_raw) if summary_raw else None
            return {"last_send_date": last_date, "last_summary": summary}
        except Exception as e:
            logger.error("Redis error fetching last run info: %s", e)
            return {"last_send_date": None, "last_summary": None, "error": str(e)}


class FileStateStore(BaseStateStore):
    """
    File-backed state store with POSIX file locking (fcntl).
    Used for local development, testing, or when Render persistent disk is attached.
    """

    def __init__(self, filepath: str = "state.json"):
        self.filepath = filepath
        self.lock_filepath = filepath + ".lock"
        self._lock_file_fd = None

    def _read_data(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            return {}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning("Could not read state file %s: %s", self.filepath, e)
            return {}

    def _write_data(self, data: Dict[str, Any]) -> None:
        tmp_path = self.filepath + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.filepath)

    def has_run_today(self, date_str: str) -> bool:
        data = self._read_data()
        return data.get("last_send_date") == date_str

    def acquire_lock(self, date_str: str) -> Tuple[bool, str]:
        if self.has_run_today(date_str):
            return False, f"Sending was already completed for today ({date_str})."

        try:
            self._lock_file_fd = open(self.lock_filepath, "w")
            if fcntl:
                # Non-blocking exclusive lock
                fcntl.flock(self._lock_file_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Double check after lock
            if self.has_run_today(date_str):
                self.release_lock("file-lock")
                return False, f"Sending was already completed for today ({date_str})."

            token = str(uuid.uuid4())
            return True, token
        except (BlockingIOError, IOError):
            if self._lock_file_fd:
                try:
                    self._lock_file_fd.close()
                except Exception:
                    pass
                self._lock_file_fd = None
            return False, "Another process or concurrent request is currently sending drafts."
        except Exception as e:
            logger.error("Error acquiring file lock: %s", e)
            return False, str(e)

    def release_lock(self, token: str) -> None:
        if self._lock_file_fd:
            try:
                if fcntl:
                    fcntl.flock(self._lock_file_fd, fcntl.LOCK_UN)
                self._lock_file_fd.close()
            except Exception as e:
                logger.error("Error releasing file lock: %s", e)
            finally:
                self._lock_file_fd = None

    def record_success(self, date_str: str, summary: Dict[str, Any]) -> None:
        data = {
            "last_send_date": date_str,
            "last_summary": summary,
            "updated_at": time.time(),
        }
        self._write_data(data)
        logger.info("Recorded successful daily send in file %s for date %s", self.filepath, date_str)

    def get_last_run_info(self) -> Dict[str, Any]:
        data = self._read_data()
        return {
            "last_send_date": data.get("last_send_date"),
            "last_summary": data.get("last_summary")
        }


def get_state_store(redis_url: Optional[str] = None, file_path: str = "state.json") -> BaseStateStore:
    """Factory to retrieve appropriate state store based on environment configuration."""
    from config import REDIS_URL, STATE_FILE_PATH

    url = redis_url or REDIS_URL
    if url:
        try:
            return RedisStateStore(url)
        except Exception as e:
            logger.warning("Failed to initialize RedisStateStore (%s). Falling back to FileStateStore.", e)

    path = file_path or STATE_FILE_PATH
    return FileStateStore(path)
