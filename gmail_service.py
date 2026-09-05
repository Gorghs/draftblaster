"""
Gmail Draft Sender module supporting DUAL AUTHENTICATION modes:
1. Gmail App Password (IMAP + SMTP)
2. Google OAuth 2.0 (Official Gmail API v1)
"""

import time
import email
import logging
import imaplib
import smtplib
from email.policy import default
from email.utils import getaddresses
from typing import Dict, Any, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    EMAIL_GMAIL_USER,
    EMAIL_GMAIL_PASSWORD,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REFRESH_TOKEN,
    GMAIL_SCOPE
)

logger = logging.getLogger("gmail_service")


# =====================================================================
# MODE 1: Gmail App Password (IMAP + SMTP)
# =====================================================================

def find_drafts_folder(mail: imaplib.IMAP4_SSL) -> str:
    """Identifies the drafts folder name in Gmail (e.g. '[Gmail]/Drafts')."""
    status, folder_list = mail.list()
    if status != "OK" or not folder_list:
        return '"[Gmail]/Drafts"'

    for folder_bytes in folder_list:
        try:
            line = folder_bytes.decode("utf-8", errors="ignore")
            if "\\Drafts" in line:
                parts = line.split(' "/" ')
                if len(parts) == 2:
                    return parts[1].strip()
        except Exception:
            continue

    return '"[Gmail]/Drafts"'


def send_drafts_via_app_password(user: str, password: str, delay_between_sends: float = 1.0) -> Dict[str, Any]:
    """Fetches and sends drafts using IMAP + SMTP with Gmail App Password."""
    logger.info("Using Gmail App Password mode for user: %s", user)
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(user, password)
    except Exception as e:
        logger.error("Failed to connect/login to Gmail IMAP: %s", e)
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": f"IMAP authentication error: {e}"}]
        }

    try:
        drafts_folder = find_drafts_folder(mail)
        select_status, _ = mail.select(drafts_folder)
        if select_status != "OK":
            mail.logout()
            return {
                "status": "failed",
                "total_drafts": 0,
                "sent": 0,
                "failed": 0,
                "errors": [{"error": f"Failed to select drafts folder: {drafts_folder}"}]
            }

        search_status, search_data = mail.search(None, "ALL")
        if search_status != "OK" or not search_data or not search_data[0]:
            mail.logout()
            return {
                "status": "completed",
                "total_drafts": 0,
                "sent": 0,
                "failed": 0,
                "message": "No drafts found in Gmail account.",
                "errors": []
            }

        mail_ids = search_data[0].split()
        total_drafts = len(mail_ids)
        if total_drafts == 0:
            mail.logout()
            return {
                "status": "completed",
                "total_drafts": 0,
                "sent": 0,
                "failed": 0,
                "message": "No drafts found in Gmail account.",
                "errors": []
            }

        logger.info("Found %d draft(s) in %s ready to send.", total_drafts, drafts_folder)

        try:
            smtp = smtplib.SMTP("smtp.gmail.com", 587)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, password)
        except Exception as e:
            mail.logout()
            return {
                "status": "failed",
                "total_drafts": total_drafts,
                "sent": 0,
                "failed": total_drafts,
                "errors": [{"error": f"SMTP connection error: {e}"}]
            }

        sent_count = 0
        failed_count = 0
        errors: List[Dict[str, Any]] = []

        try:
            for idx, mail_id in enumerate(mail_ids, start=1):
                msg_id_str = mail_id.decode("utf-8", errors="ignore")
                try:
                    fetch_status, msg_data = mail.fetch(mail_id, "(RFC822)")
                    if fetch_status != "OK" or not msg_data or not msg_data[0]:
                        failed_count += 1
                        errors.append({"draft_id": msg_id_str, "error": "Failed to fetch draft data"})
                        continue

                    raw_bytes = msg_data[0][1]
                    msg = email.message_from_bytes(raw_bytes, policy=default)

                    subject = str(msg.get("Subject", "(No Subject)"))
                    recipients = []
                    for header_name in ["To", "Cc", "Bcc"]:
                        val = msg.get(header_name)
                        if val:
                            parsed = getaddresses([str(val)])
                            for _, addr in parsed:
                                if addr and addr not in recipients:
                                    recipients.append(addr)

                    if not recipients:
                        failed_count += 1
                        errors.append({"draft_id": msg_id_str, "error": "No recipient addresses found"})
                        continue

                    logger.info("[%d/%d] Sending Draft %s | To: %s | Subject: %s", idx, total_drafts, msg_id_str, ", ".join(recipients), subject)
                    smtp.send_message(msg)
                    sent_count += 1

                    # Remove draft from Drafts folder
                    mail.store(mail_id, "+FLAGS", "\\Deleted")

                    if delay_between_sends > 0:
                        time.sleep(delay_between_sends)

                except Exception as err:
                    failed_count += 1
                    logger.error("Error sending draft %s: %s", msg_id_str, err)
                    errors.append({"draft_id": msg_id_str, "error": str(err)})

            mail.expunge()
        finally:
            try:
                smtp.quit()
            except Exception:
                pass

        mail.logout()

        return {
            "status": "completed" if failed_count == 0 else "partial_success",
            "auth_method": "app_password",
            "total_drafts": total_drafts,
            "sent": sent_count,
            "failed": failed_count,
            "errors": errors
        }

    except Exception as e:
        logger.error("Unexpected error in App Password mode: %s", e)
        try:
            mail.logout()
        except Exception:
            pass
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": str(e)}]
        }


# =====================================================================
# MODE 2: Google OAuth 2.0 (Official Gmail API v1)
# =====================================================================

def send_drafts_via_oauth(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    delay_between_sends: float = 1.0
) -> Dict[str, Any]:
    """Fetches and sends drafts using official Gmail API v1 with OAuth 2.0 refresh token."""
    logger.info("Using official Google OAuth 2.0 mode.")
    try:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[GMAIL_SCOPE]
        )
        creds.refresh(Request())
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    except Exception as e:
        logger.error("OAuth authentication failed: %s", e)
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": f"OAuth initialization error: {e}"}]
        }

    all_drafts = []
    page_token = None
    try:
        while True:
            resp = service.users().drafts().list(userId="me", pageToken=page_token).execute()
            drafts = resp.get("drafts", [])
            all_drafts.extend(drafts)
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
    except Exception as e:
        logger.error("Error querying drafts via Gmail API: %s", e)
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": str(e)}]
        }

    total_count = len(all_drafts)
    if total_count == 0:
        return {
            "status": "completed",
            "auth_method": "oauth2",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "message": "No drafts found in Gmail account.",
            "errors": []
        }

    sent_count = 0
    failed_count = 0
    errors = []

    for idx, draft in enumerate(all_drafts, start=1):
        draft_id = draft.get("id")
        if not draft_id:
            continue
        try:
            logger.info("[%d/%d] Sending Draft ID: %s via Gmail API", idx, total_count, draft_id)
            service.users().drafts().send(userId="me", body={"id": draft_id}).execute()
            sent_count += 1
            if delay_between_sends > 0:
                time.sleep(delay_between_sends)
        except Exception as err:
            failed_count += 1
            logger.error("Error sending draft %s: %s", draft_id, err)
            errors.append({"draft_id": draft_id, "error": str(err)})

    return {
        "status": "completed" if failed_count == 0 else "partial_success",
        "auth_method": "oauth2",
        "total_drafts": total_count,
        "sent": sent_count,
        "failed": failed_count,
        "errors": errors
    }


# =====================================================================
# Main Unified Dispatcher
# =====================================================================

def send_all_drafts(
    user: Optional[str] = None,
    password: Optional[str] = None,
    delay_between_sends: float = 1.0
) -> Dict[str, Any]:
    """
    Unified entrypoint: Automatically detects whether to use App Password
    or Google OAuth based on available environment credentials.
    """
    u = EMAIL_GMAIL_USER if user is None else user
    p = EMAIL_GMAIL_PASSWORD if password is None else password

    # 1. Prefer App Password if provided
    if u and p:
        return send_drafts_via_app_password(u, p, delay_between_sends=delay_between_sends)

    # 2. Otherwise fallback to OAuth 2.0 if configured
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REFRESH_TOKEN:
        return send_drafts_via_oauth(
            GOOGLE_CLIENT_ID,
            GOOGLE_CLIENT_SECRET,
            GOOGLE_REFRESH_TOKEN,
            delay_between_sends=delay_between_sends
        )

    # 3. Neither configured
    err = "No authentication configured. Provide either (EMAIL_GMAIL_USER + EMAIL_GMAIL_PASSWORD) or Google OAuth (GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET + GOOGLE_REFRESH_TOKEN)."
    logger.error(err)
    return {
        "status": "failed",
        "total_drafts": 0,
        "sent": 0,
        "failed": 0,
        "errors": [{"error": err}]
    }
