"""
Configuration module for Gmail Draft Auto-Sender.
Supports DUAL AUTHENTICATION modes:
1. Gmail App Password (IMAP/SMTP)
2. Google OAuth 2.0 (Official Gmail API v1)
"""

import os
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("config")

# Web Server Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Method 1: Gmail App Password Credentials
EMAIL_GMAIL_USER = os.getenv("EMAIL_GMAIL_USER", "")
EMAIL_GMAIL_PASSWORD = os.getenv("EMAIL_GMAIL_PASSWORD", "").replace(" ", "")

# Method 2: Google OAuth 2.0 Credentials
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID") or os.getenv("GMAIL_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET") or os.getenv("GMAIL_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN") or os.getenv("GMAIL_REFRESH_TOKEN", "")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "https://draftblaster.onrender.com/oauth/callback")
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
EXECUTION_WINDOW_MINUTES = int(os.getenv("EXECUTION_WINDOW_MINUTES", "5"))

# Security Secret to protect /trigger endpoint
TRIGGER_SECRET = os.getenv("TRIGGER_SECRET", "")

# State Persistence & Concurrency Locking
REDIS_URL = os.getenv("REDIS_URL", "")
STATE_FILE_PATH = os.getenv("STATE_FILE_PATH", "state.json")
