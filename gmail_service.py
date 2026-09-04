"""
Gmail service module for authenticating via OAuth 2.0 refresh token
and sending all available Gmail drafts with pagination, error resilience, and structured reporting.
"""

import time
import logging
from typing import Dict, Any, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REFRESH_TOKEN,
    GMAIL_SCOPE
)

logger = logging.getLogger("gmail_service")


class GmailServiceError(Exception):
    """Base exception for Gmail service errors."""
    pass


class MissingCredentialsError(GmailServiceError):
    """Raised when required Google OAuth credentials are not configured."""
    pass


def get_gmail_client(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    refresh_token: Optional[str] = None
) -> Resource:
    """
    Constructs an authenticated Gmail API v1 service instance using the OAuth refresh token.
    Works unattended without requiring persistent token files or repeated user logins.
    """
    cid = client_id or GOOGLE_CLIENT_ID
    csec = client_secret or GOOGLE_CLIENT_SECRET
    rtoken = refresh_token or GOOGLE_REFRESH_TOKEN

    if not cid or not csec or not rtoken:
        missing = []
        if not cid:
            missing.append("GOOGLE_CLIENT_ID")
        if not csec:
            missing.append("GOOGLE_CLIENT_SECRET")
        if not rtoken:
            missing.append("GOOGLE_REFRESH_TOKEN")
        error_msg = f"Missing required Google OAuth credentials in environment: {', '.join(missing)}"
        logger.error(error_msg)
        raise MissingCredentialsError(error_msg)

    try:
        # Construct credentials directly from refresh token
        creds = Credentials(
            token=None,
            refresh_token=rtoken,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=cid,
            client_secret=csec,
            scopes=[GMAIL_SCOPE]
        )

        # Refresh immediately to test validity and obtain fresh access token
        creds.refresh(Request())
        logger.info("Successfully refreshed Google OAuth access token using refresh token.")

        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        return service
    except Exception as e:
        logger.error("Failed to authenticate with Gmail API via refresh token: %s", e)
        raise GmailServiceError(f"OAuth authentication failed: {e}") from e


def get_draft_metadata(service: Resource, draft_id: str) -> Dict[str, str]:
    """Retrieves basic metadata (Subject, To) for a draft for logging purposes."""
    try:
        draft = service.users().drafts().get(userId="me", id=draft_id, format="metadata").execute()
        headers = draft.get("message", {}).get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "(No Subject)")
        to_addr = next((h["value"] for h in headers if h["name"].lower() == "to"), "(No Recipient)")
        return {"subject": subject, "to": to_addr}
    except Exception:
        return {"subject": "(Draft)", "to": "(Recipient)"}


def send_all_drafts(
    service: Optional[Resource] = None,
    delay_between_sends: float = 1.0
) -> Dict[str, Any]:
    """
    Retrieves and sends ALL existing Gmail drafts.
    
    1. Authenticates using OAuth refresh token (if service is not pre-injected).
    2. Handles pagination to retrieve all drafts across all pages.
    3. If zero drafts, returns a clean success response.
    4. Iterates through all drafts and sends them via users().drafts().send().
    5. Recovers from individual draft failures and continues sending remaining drafts.
    6. Returns a structured execution summary.
    """
    if service is None:
        service = get_gmail_client()

    logger.info("Querying all drafts from Gmail account...")
    all_drafts: List[Dict[str, Any]] = []
    page_token: Optional[str] = None

    try:
        # Step 1: Paginate and collect all draft IDs
        while True:
            response = service.users().drafts().list(
                userId="me",
                pageToken=page_token
            ).execute()

            drafts = response.get("drafts", [])
            all_drafts.extend(drafts)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

    except HttpError as http_err:
        logger.error("Gmail API HTTP error listing drafts: %s", http_err)
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": f"Gmail API list error: {http_err}"}]
        }
    except Exception as err:
        logger.error("Unexpected error querying drafts: %s", err)
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": str(err)}]
        }

    total_count = len(all_drafts)
    if total_count == 0:
        logger.info("No drafts found in Gmail account. Nothing to send.")
        return {
            "status": "completed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "message": "No drafts found in Gmail account.",
            "errors": []
        }

    logger.info("Found %d draft(s) ready to send.", total_count)
    sent_count = 0
    failed_count = 0
    errors: List[Dict[str, Any]] = []

    # Step 2: Iterate and send each draft
    for idx, draft in enumerate(all_drafts, start=1):
        draft_id = draft.get("id")
        if not draft_id:
            continue

        meta = get_draft_metadata(service, draft_id)
        logger.info(
            "[%d/%d] Sending Draft ID: %s | To: %s | Subject: %s",
            idx, total_count, draft_id, meta["to"], meta["subject"]
        )

        try:
            # Send draft via Gmail API
            service.users().drafts().send(
                userId="me",
                body={"id": draft_id}
            ).execute()

            sent_count += 1
            logger.info("Successfully sent Draft ID %s", draft_id)

            # Safety pacing delay between sends
            if delay_between_sends > 0:
                time.sleep(delay_between_sends)

        except HttpError as http_err:
            failed_count += 1
            err_msg = f"HTTP {http_err.resp.status}: {http_err.error_details if hasattr(http_err, 'error_details') else str(http_err)}"
            logger.error("Failed to send draft %s: %s", draft_id, err_msg)
            errors.append({"draft_id": draft_id, "error": err_msg})

        except Exception as err:
            failed_count += 1
            logger.error("Unexpected error sending draft %s: %s", draft_id, err)
            errors.append({"draft_id": draft_id, "error": str(err)})

    logger.info(
        "Finished draft execution: %d total, %d sent, %d failed.",
        total_count, sent_count, failed_count
    )

    return {
        "status": "completed" if failed_count == 0 else "partial_success",
        "total_drafts": total_count,
        "sent": sent_count,
        "failed": failed_count,
        "errors": errors
    }
