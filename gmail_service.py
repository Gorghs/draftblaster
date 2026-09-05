"""
Gmail Draft Sender module using Gmail App Password (IMAP + SMTP).
Eliminates Google Cloud Console, OAuth clients, redirect URIs, and token expirations.
Reads existing drafts from [Gmail]/Drafts via IMAP, sends them via SMTP, and removes them from drafts.
"""

import time
import email
import logging
import imaplib
import smtplib
from email.policy import default
from email.utils import getaddresses
from typing import Dict, Any, List, Optional, Tuple

from config import (
    EMAIL_GMAIL_USER,
    EMAIL_GMAIL_PASSWORD
)

logger = logging.getLogger("gmail_service")


class GmailAuthError(Exception):
    """Raised when authentication with Gmail fails."""
    pass


def find_drafts_folder(mail: imaplib.IMAP4_SSL) -> str:
    """
    Identifies the drafts folder name in Gmail.
    In English Gmail, it's typically '[Gmail]/Drafts', but this dynamically detects
    the folder with the '\\Drafts' attribute to support any localized account.
    """
    status, folder_list = mail.list()
    if status != "OK" or not folder_list:
        return '"[Gmail]/Drafts"'

    for folder_bytes in folder_list:
        try:
            line = folder_bytes.decode("utf-8", errors="ignore")
            if "\\Drafts" in line:
                # Format: (\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"
                parts = line.split(' "/" ')
                if len(parts) == 2:
                    return parts[1].strip()
        except Exception:
            continue

    return '"[Gmail]/Drafts"'


def send_all_drafts(
    user: Optional[str] = None,
    password: Optional[str] = None,
    delay_between_sends: float = 1.0
) -> Dict[str, Any]:
    """
    Connects to Gmail via IMAP and SMTP using App Password:
    1. Connects to imap.gmail.com:993 and opens Drafts folder.
    2. Searches for all existing drafts.
    3. If zero drafts, returns a clean completed response.
    4. Connects to smtp.gmail.com:587.
    5. Sends each draft message and removes the draft from [Gmail]/Drafts upon success.
    6. Returns structured summary.
    """
    gmail_user = user or EMAIL_GMAIL_USER
    gmail_pass = password or EMAIL_GMAIL_PASSWORD

    if not gmail_user or not gmail_pass:
        err_msg = "Missing EMAIL_GMAIL_USER or EMAIL_GMAIL_PASSWORD. Please configure them in environment variables."
        logger.error(err_msg)
        return {
            "status": "failed",
            "total_drafts": 0,
            "sent": 0,
            "failed": 0,
            "errors": [{"error": err_msg}]
        }

    # Step 1: Connect to IMAP to fetch drafts
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(gmail_user, gmail_pass)
        logger.info("Successfully authenticated with Gmail IMAP for user %s", gmail_user)
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
        select_status, select_data = mail.select(drafts_folder)
        if select_status != "OK":
            logger.error("Could not open Gmail drafts folder %s", drafts_folder)
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
            logger.info("No drafts found in %s.", drafts_folder)
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
            logger.info("No drafts found in %s.", drafts_folder)
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

        # Step 2: Connect to SMTP to send the emails
        try:
            smtp = smtplib.SMTP("smtp.gmail.com", 587)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(gmail_user, gmail_pass)
            logger.info("Successfully connected to Gmail SMTP.")
        except Exception as e:
            logger.error("Failed to connect/login to Gmail SMTP: %s", e)
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
                        errors.append({"draft_id": msg_id_str, "error": "Failed to fetch draft data via IMAP"})
                        continue

                    raw_bytes = msg_data[0][1]
                    msg = email.message_from_bytes(raw_bytes, policy=default)

                    # Extract recipients from To, Cc, Bcc
                    subject = str(msg.get("Subject", "(No Subject)"))
                    recipients = []
                    for header_name in ["To", "Cc", "Bcc"]:
                        val = msg.get(header_name)
                        if val:
                            parsed_addresses = getaddresses([str(val)])
                            for name, addr in parsed_addresses:
                                if addr and addr not in recipients:
                                    recipients.append(addr)

                    if not recipients:
                        logger.warning("[%d/%d] Draft ID %s has no recipient addresses. Skipping.", idx, total_drafts, msg_id_str)
                        failed_count += 1
                        errors.append({"draft_id": msg_id_str, "error": "No recipients specified in draft"})
                        continue

                    logger.info(
                        "[%d/%d] Sending Draft ID: %s | To: %s | Subject: %s",
                        idx, total_drafts, msg_id_str, ", ".join(recipients), subject
                    )

                    # Send via SMTP
                    smtp.send_message(msg)
                    sent_count += 1
                    logger.info("Successfully sent Draft ID %s", msg_id_str)

                    # Mark draft as deleted in IMAP so it doesn't stay in Drafts
                    mail.store(mail_id, "+FLAGS", "\\Deleted")

                    if delay_between_sends > 0:
                        time.sleep(delay_between_sends)

                except Exception as err:
                    failed_count += 1
                    logger.error("Error sending draft %s: %s", msg_id_str, err)
                    errors.append({"draft_id": msg_id_str, "error": str(err)})

            # Expunge deleted drafts from IMAP
            mail.expunge()

        finally:
            try:
                smtp.quit()
            except Exception:
                pass

        mail.logout()

        logger.info(
            "Draft send batch finished: %d total, %d sent, %d failed.",
            total_drafts, sent_count, failed_count
        )

        return {
            "status": "completed" if failed_count == 0 else "partial_success",
            "total_drafts": total_drafts,
            "sent": sent_count,
            "failed": failed_count,
            "errors": errors
        }

    except Exception as e:
        logger.error("Unexpected error during draft processing: %s", e)
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
