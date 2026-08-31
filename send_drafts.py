#!/usr/bin/env python3
"""
Gmail Drafts Auto-Sender & 9:00 AM Daily Scheduler
=================================================
Automates sending all existing Gmail drafts using the official Google Gmail API (v1)
with OAuth 2.0 authentication and token management.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('GmailDraftSender')

# If modifying these scopes, delete the file token.json.
# Full Gmail scope is required to read, compose, and send drafts.
SCOPES = ['https://mail.google.com/']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'


def load_env_file(filepath='.env'):
    """Simple parser to load .env variables into os.environ if present."""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key and val and key not in os.environ:
                        os.environ[key] = val


def get_gmail_service():
    """
    Handles OAuth 2.0 authentication and initializes the Gmail v1 API service.
    
    1. Checks for local 'token.json' or GMAIL_TOKEN_JSON environment variable.
    2. Refreshes the token if expired.
    3. Initiates authentication flow via 'credentials.json' or GMAIL_CLIENT_ID / GMAIL_CLIENT_SECRET.
    4. Saves valid credentials to 'token.json' for subsequent runs.
    
    Returns:
        googleapiclient.discovery.Resource: Authenticated Gmail API service object.
    """
    load_env_file()
    creds = None

    # Step 1: Check if token.json exists or GMAIL_TOKEN_JSON in environment
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            logger.info("Loaded credentials from %s", TOKEN_FILE)
        except Exception as e:
            logger.warning("Failed to load %s: %s. Initiating new authorization flow.", TOKEN_FILE, e)
            creds = None
    elif os.environ.get('GMAIL_TOKEN_JSON'):
        try:
            token_info = json.loads(os.environ['GMAIL_TOKEN_JSON'])
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
            logger.info("Loaded credentials from GMAIL_TOKEN_JSON environment variable.")
        except Exception as e:
            logger.warning("Failed to parse GMAIL_TOKEN_JSON: %s", e)
            creds = None

    # Step 2: Refresh token or initiate local OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired OAuth token...")
                creds.refresh(Request())
                logger.info("Token successfully refreshed.")
            except Exception as e:
                logger.warning("Token refresh failed: %s. Re-authenticating.", e)
                creds = None

        if not creds or not creds.valid:
            client_id = os.environ.get('GMAIL_CLIENT_ID')
            client_secret = os.environ.get('GMAIL_CLIENT_SECRET')

            if os.path.exists(CREDENTIALS_FILE):
                logger.info("Starting authentication flow via %s...", CREDENTIALS_FILE)
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            elif client_id and client_secret:
                logger.info("Starting authentication flow using client credentials from .env...")
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["http://localhost"]
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            else:
                raise FileNotFoundError(
                    f"Required OAuth client credentials not found.\n"
                    f"Either provide '{CREDENTIALS_FILE}' or define GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in .env."
                )

            creds = flow.run_local_server(port=0)
            logger.info("OAuth Authentication successful.")

        # Save credentials for subsequent runs with restricted user permissions
        try:
            with open(TOKEN_FILE, 'w', encoding='utf-8') as token:
                token.write(creds.to_json())
            try:
                os.chmod(TOKEN_FILE, 0o600)
            except Exception:
                pass
            logger.info("Saved valid authorization credentials to %s (chmod 600)", TOKEN_FILE)
        except Exception as e:
            logger.error("Failed to write to %s: %s", TOKEN_FILE, e)

    # Step 3: Build Gmail v1 Service
    try:
        service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        logger.error("Failed to build Gmail service: %s", e)
        raise


def get_draft_details(service, draft_id):
    """
    Retrieves metadata (Subject, Recipient) for a specific draft for logging.
    """
    try:
        draft = service.users().drafts().get(userId='me', id=draft_id, format='metadata').execute()
        headers = draft.get('message', {}).get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
        to_addr = next((h['value'] for h in headers if h['name'].lower() == 'to'), '(Unknown Recipient)')
        return {'subject': subject, 'to': to_addr}
    except Exception:
        return {'subject': '(Draft)', 'to': '(Recipient)'}


def send_all_drafts():
    """
    Fetches all existing Gmail drafts and sends each one sequentially.
    """
    logger.info("=" * 60)
    logger.info("Starting Gmail Drafts Sending Task at %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logger.info("=" * 60)

    try:
        service = get_gmail_service()
    except Exception as e:
        logger.critical("Aborting draft sending: could not initialize Gmail service: %s", e)
        return

    try:
        # Step 4: List all available drafts in user's account
        drafts_list = []
        page_token = None

        while True:
            response = service.users().drafts().list(
                userId='me',
                pageToken=page_token
            ).execute()

            drafts = response.get('drafts', [])
            drafts_list.extend(drafts)

            page_token = response.get('nextPageToken')
            if not page_token:
                break

        total_drafts = len(drafts_list)
        if total_drafts == 0:
            logger.info("No drafts found in your Gmail account. Nothing to send.")
            return

        logger.info("Found %d draft(s) ready to send.", total_drafts)

        sent_count = 0
        failed_count = 0

        # Step 5: Iterate through retrieved drafts and execute service.users().drafts().send()
        for idx, draft in enumerate(drafts_list, start=1):
            draft_id = draft.get('id')
            if not draft_id:
                continue

            details = get_draft_details(service, draft_id)
            logger.info("[%d/%d] Sending Draft ID: %s | To: %s | Subject: %s",
                        idx, total_drafts, draft_id, details['to'], details['subject'])

            try:
                # Execute send
                sent_msg = service.users().drafts().send(
                    userId='me',
                    body={'id': draft_id}
                ).execute()

                sent_count += 1
                msg_id = sent_msg.get('id', 'N/A')
                logger.info("Successfully sent Draft ID: %s (Message ID: %s)", draft_id, msg_id)

                # Pacing delay between sends to adhere to good sending practices
                time.sleep(1.5)

            except HttpError as http_err:
                failed_count += 1
                logger.error("HTTP Error sending Draft ID %s: %s", draft_id, http_err)
            except Exception as err:
                failed_count += 1
                logger.error("Unexpected error sending Draft ID %s: %s", draft_id, err)

        logger.info("-" * 60)
        logger.info("Batch summary: %d draft(s) processed | %d sent successfully | %d failed.",
                    total_drafts, sent_count, failed_count)
        logger.info("-" * 60)

    except HttpError as http_err:
        logger.error("Gmail API Error while querying drafts: %s", http_err)
    except Exception as e:
        logger.error("An unexpected error occurred during draft processing: %s", e)


def run_scheduler(schedule_time="09:00"):
    """
    Schedules the script to run everyday at the specified time (e.g. 09:00 AM).
    """
    logger.info("Starting Daily Scheduler daemon. Target execution time: %s every day.", schedule_time)
    schedule.every().day.at(schedule_time).do(send_all_drafts)

    logger.info("Scheduler active. Press Ctrl+C to stop.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
            break
        except Exception as e:
            logger.error("Scheduler encountered an error: %s", e)
            time.sleep(60)


def main():
    parser = argparse.ArgumentParser(
        description="Automate sending Gmail drafts via official Gmail API v1."
    )
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run in daemon scheduler mode (runs automatically every day).'
    )
    parser.add_argument(
        '--time',
        type=str,
        default='09:00',
        help='Time in 24-hour HH:MM format for daily scheduling (default: 09:00).'
    )
    parser.add_argument(
        '--now',
        action='store_true',
        help='Send all existing drafts immediately.'
    )

    args = parser.parse_args()

    if args.schedule:
        if args.now:
            send_all_drafts()
        run_scheduler(schedule_time=args.time)
    else:
        # Default action: run immediately (ideal for system cron jobs, serverless triggers, or manual runs)
        send_all_drafts()


if __name__ == '__main__':
    main()
