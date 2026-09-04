"""
Configuration module for Gmail Draft Auto-Sender.
Loads and validates environment variables.
"""

import os
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dotenv import load_dotenv

# Load local .env file if available
load_dotenv()

logger = logging.getLogger("config")

# Web Server Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN", "")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")

# Least-privileged scope: permits creating, reading, listing, and sending drafts.
# Does NOT permit reading entire inbox messages, modifying labels, or deleting mailbox emails.
GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.compose"

# Timezone & Scheduling
TIMEZONE_STR = os.getenv("TIMEZONE", "Asia/Kolkata")
try:
    APP_TIMEZONE = ZoneInfo(TIMEZONE_STR)
except ZoneInfoNotFoundError:
    logger.warning("Invalid TIMEZONE '%s'. Falling back to 'Asia/Kolkata'", TIMEZONE_STR)
    TIMEZONE_STR = "Asia/Kolkata"
    APP_TIMEZONE = ZoneInfo("Asia/Kolkata")

SEND_HOUR = int(os.getenv("SEND_HOUR", "9"))
SEND_MINUTE = int(os.getenv("SEND_MINUTE", "0"))

# Allowed execution window (in minutes) after SEND_HOUR:SEND_MINUTE
# E.g., if SEND_HOUR=9, SEND_MINUTE=0, WINDOW=5, calls between 09:00 and 09:05 qualify.
EXECUTION_WINDOW_MINUTES = int(os.getenv("EXECUTION_WINDOW_MINUTES", "5"))

# Optional Security Secret for /trigger endpoint
TRIGGER_SECRET = os.getenv("TRIGGER_SECRET", "")

# State Persistence & Concurrency Locking
# Redis URL (e.g. from Upstash Redis or Render Redis) for multi-worker / multi-restart persistence
REDIS_URL = os.getenv("REDIS_URL", "")
STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", "state.json")
