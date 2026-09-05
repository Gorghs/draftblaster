#!/usr/bin/env python3
"""
Test script to send exactly 5 drafts and verify end-to-end functionality.
"""

import os
import time
import email
import imaplib
import smtplib
from email.policy import default
from email.utils import getaddresses
from dotenv import load_dotenv

from gmail_service import find_drafts_folder

load_dotenv()

USER = os.getenv("EMAIL_GMAIL_USER")
PASSWORD = os.getenv("EMAIL_GMAIL_PASSWORD")
LIMIT = 5

def main():
    if not USER or not PASSWORD:
        print("ERROR: EMAIL_GMAIL_USER or EMAIL_GMAIL_PASSWORD not set in .env")
        return

    print("=" * 70)
    print(f"Connecting to Gmail as {USER}...")
    print("=" * 70)

    # 1. Connect to IMAP
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login(USER, PASSWORD)
    
    drafts_folder = find_drafts_folder(mail)
    mail.select(drafts_folder)
    
    status, data = mail.search(None, "ALL")
    mail_ids = data[0].split()
    total_found = len(mail_ids)
    print(f"Total drafts found in {drafts_folder}: {total_found}")

    if total_found == 0:
        print("No drafts to send.")
        mail.logout()
        return

    target_ids = mail_ids[:LIMIT]
    print(f"Proceeding to send the first {len(target_ids)} draft(s)...\n")

    # 2. Connect to SMTP
    smtp = smtplib.SMTP("smtp.gmail.com", 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(USER, PASSWORD)

    sent_count = 0
    failed_count = 0

    try:
        for idx, m_id in enumerate(target_ids, start=1):
            m_id_str = m_id.decode("utf-8", errors="ignore")
            status, msg_data = mail.fetch(m_id, "(RFC822)")
            if status != "OK" or not msg_data or not msg_data[0]:
                print(f"[{idx}/{LIMIT}] Failed to fetch draft ID: {m_id_str}")
                failed_count += 1
                continue

            raw_bytes = msg_data[0][1]
            msg = email.message_from_bytes(raw_bytes, policy=default)

            subject = str(msg.get("Subject", "(No Subject)"))
            recipients = []
            for header_name in ["To", "Cc", "Bcc"]:
                val = msg.get(header_name)
                if val:
                    for _, addr in getaddresses([str(val)]):
                        if addr and addr not in recipients:
                            recipients.append(addr)

            if not recipients:
                print(f"[{idx}/{LIMIT}] Draft ID {m_id_str} has no recipients. Skipping.")
                failed_count += 1
                continue

            print(f"[{idx}/{LIMIT}] Sending Draft ID: {m_id_str}")
            print(f"       To:      {', '.join(recipients)}")
            print(f"       Subject: {subject}")

            try:
                smtp.send_message(msg)
                sent_count += 1
                print(f"       Status:  ✓ SENT SUCCESSFULLY")

                # Mark as deleted in IMAP so it leaves Drafts
                mail.store(m_id, "+FLAGS", "\\Deleted")

                # Pacing delay between sends
                time.sleep(1.5)

            except Exception as e:
                failed_count += 1
                print(f"       Status:  ✗ FAILED: {e}")

        # Expunge deleted drafts from IMAP
        mail.expunge()

    finally:
        try:
            smtp.quit()
        except Exception:
            pass
        try:
            mail.logout()
        except Exception:
            pass

    print("\n" + "=" * 70)
    print(f"BATCH SUMMARY: {sent_count} sent successfully | {failed_count} failed | Remaining drafts: {total_found - sent_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
