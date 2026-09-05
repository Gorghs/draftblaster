#!/usr/bin/env python3
"""
Draftblaster: Standalone One-Time Gmail Draft Auto-Sender.
Designed for scheduled GitHub Actions runs and local execution.

Execution flow:
1. Load environment variables (supports .env for local use).
2. Validate credentials before connecting.
3. Fetch all current drafts via IMAP.
4. Send each draft via SMTP (or log them in --dry-run mode).
5. Remove sent drafts from Drafts folder.
6. Print execution summary and exit cleanly with appropriate status code.
"""

import sys
import os
import argparse
import logging
from dotenv import load_dotenv

# Ensure local .env is loaded if present
load_dotenv()

from gmail_service import send_all_drafts

# Configure logging to standard output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("send_drafts")


def mask_email(email_str: str) -> str:
    """Mask email for safe logging (e.g. th***@gmail.com)."""
    if not email_str or "@" not in email_str:
        return "***"
    local, domain = email_str.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[:2] + "*" * (len(local) - 2)
    return f"{masked_local}@{domain}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Draftblaster: Send all pending Gmail drafts once and exit."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect and list drafts without sending or deleting them."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between sending consecutive drafts (default: 1.0s)."
    )

    args = parser.parse_args()

    user = os.getenv("EMAIL_GMAIL_USER", "").strip()
    password = os.getenv("EMAIL_GMAIL_PASSWORD", "").strip().replace(" ", "")

    logger.info("=" * 60)
    logger.info("Draftblaster - One-Time Gmail Draft Auto-Sender")
    logger.info("=" * 60)

    # Validate required credentials before connecting
    if not user or not password:
        logger.error("Missing required credentials:")
        if not user:
            logger.error("  - EMAIL_GMAIL_USER is not set.")
        if not password:
            logger.error("  - EMAIL_GMAIL_PASSWORD is not set.")
        logger.error("Please configure these in GitHub Secrets or in a local .env file.")
        return 1

    masked = mask_email(user)
    logger.info("Target Gmail Account: %s", masked)
    if args.dry_run:
        logger.info("Mode: DRY-RUN (safe inspection; no emails sent or deleted)")
    else:
        logger.info("Mode: LIVE (drafts will be sent via SMTP and deleted from Drafts)")

    # Execute one-time sending workflow
    try:
        results = send_all_drafts(
            user=user,
            password=password,
            delay_between_sends=args.delay,
            dry_run=args.dry_run
        )
    except Exception as exc:
        logger.exception("Fatal unexpected error during execution: %s", exc)
        return 1

    status = results.get("status", "failed")
    total = results.get("total_drafts", 0)
    sent = results.get("sent", 0)
    failed = results.get("failed", 0)
    errors = results.get("errors", [])

    logger.info("-" * 60)
    logger.info("EXECUTION SUMMARY:")
    logger.info("  Status:       %s", status.upper())
    logger.info("  Total Drafts: %d", total)
    if args.dry_run:
        logger.info("  Action:       INSPECTED (DRY RUN)")
    else:
        logger.info("  Sent:         %d", sent)
        logger.info("  Failed:       %d", failed)

    if errors:
        logger.error("Encountered %d error(s):", len(errors))
        for idx, err in enumerate(errors, start=1):
            draft_id = f" (Draft ID: {err.get('draft_id')})" if "draft_id" in err else ""
            logger.error("  [%d] %s%s", idx, err.get("error", "Unknown error"), draft_id)

    logger.info("=" * 60)

    # Return non-zero exit code on real failure
    if status == "failed" or failed > 0:
        logger.error("Job finished with errors. Exiting with code 1.")
        return 1

    logger.info("Job finished successfully. Exiting with code 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
