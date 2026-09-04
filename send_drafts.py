#!/usr/bin/env python3
"""
CLI Utility for Gmail Draft Auto-Sender.
Allows manual testing, trigger evaluation, and one-time runs from the command line.
"""

import argparse
import json
import logging
from scheduler import evaluate_and_trigger
from gmail_service import send_all_drafts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("cli")


def main():
    parser = argparse.ArgumentParser(description="Gmail Draft Auto-Sender CLI")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Bypass schedule time check and send drafts immediately."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check whether current time falls within scheduled execution window."
    )

    args = parser.parse_args()

    if args.now:
        logger.info("Executing immediate send...")
        result = evaluate_and_trigger(force=True)
        print(json.dumps(result, indent=2))
    elif args.check:
        logger.info("Checking schedule status...")
        result = evaluate_and_trigger(force=False)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
