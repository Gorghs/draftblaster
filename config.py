"""
Configuration module for Gmail Draft Auto-Sender.
Supports App Password authentication (IMAP/SMTP) as primary method,
with fallback for OAuth 2.0 if configured.
"""

import os
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dotenv import load_dotenv

# Load local .env file
load_dotenv()

logger = logging.getLogger("config")

# Web Server Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Gmail App Password Credentials (Simplest & Recommended: No GCP/OAuth required)
EMAIL_GMAIL_USER = os.getenv("EMAIL_GMAIL_USER", "")
EMAIL_GMAIL_PASSWORD = os.getenv("EMAIL_GMAIL_PASSWORD", "").replace(" ", "")

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
EXECUTION_WINDOW_MINUTES = int(os.getenv("EXECUTION_WINDOW_MINUTES", "5"))

# Optional Secret to protect /trigger endpoint
TRIGGER_SECRET = os.getenv("TRIGGER_SECRET", "")

# State Persistence & Concurrency Locking
REDIS_URL = os.getenv("REDIS_URL", "")
STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", "state.json")
