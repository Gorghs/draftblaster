"""
Unit tests for App Password based Gmail draft fetching and sending (IMAP + SMTP).
All IMAP and SMTP network connections are strictly mocked.
"""

from unittest.mock import MagicMock, patch
import pytest

from gmail_service import send_all_drafts


def test_no_drafts_found():
    """Verify clean handling when no drafts are in Gmail."""
    mock_imap = MagicMock()
    mock_imap.list.return_value = ("OK", [b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"'])
    mock_imap.select.return_value = ("OK", [b"0"])
    mock_imap.search.return_value = ("OK", [b""])

    with patch("imaplib.IMAP4_SSL", return_value=mock_imap):
        result = send_all_drafts(user="test@gmail.com", password="app-password", delay_between_sends=0)

        assert result["status"] == "completed"
        assert result["total_drafts"] == 0
        assert result["sent"] == 0
        assert result["failed"] == 0
        assert "No drafts found" in result["message"]


def test_multiple_drafts_sent():
    """Verify all drafts are fetched via IMAP, sent via SMTP, and marked deleted."""
    mock_imap = MagicMock()
    mock_imap.list.return_value = ("OK", [b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"'])
    mock_imap.select.return_value = ("OK", [b"2"])
    mock_imap.search.return_value = ("OK", [b"1 2"])

    sample_email = b"From: me@gmail.com\r\nTo: recipient@example.com\r\nSubject: Hello\r\n\r\nDraft content"
    mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {50})", sample_email)])

    mock_smtp = MagicMock()

    with patch("imaplib.IMAP4_SSL", return_value=mock_imap), \
         patch("smtplib.SMTP", return_value=mock_smtp):
        result = send_all_drafts(user="test@gmail.com", password="app-password", delay_between_sends=0)

        assert result["status"] == "completed"
        assert result["total_drafts"] == 2
        assert result["sent"] == 2
        assert result["failed"] == 0
        assert mock_smtp.send_message.call_count == 2
        assert mock_imap.store.call_count == 2
        mock_imap.expunge.assert_called_once()


def test_one_draft_fails_others_succeed():
    """Verify that a failure on one draft does not block subsequent drafts."""
    mock_imap = MagicMock()
    mock_imap.list.return_value = ("OK", [b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"'])
    mock_imap.select.return_value = ("OK", [b"2"])
    mock_imap.search.return_value = ("OK", [b"1 2"])

    sample_email = b"From: me@gmail.com\r\nTo: recipient@example.com\r\nSubject: Test\r\n\r\nDraft content"
    mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {50})", sample_email)])

    mock_smtp = MagicMock()
    # First send raises Exception, second succeeds
    mock_smtp.send_message.side_effect = [Exception("SMTP temporary failure"), None]

    with patch("imaplib.IMAP4_SSL", return_value=mock_imap), \
         patch("smtplib.SMTP", return_value=mock_smtp):
        result = send_all_drafts(user="test@gmail.com", password="app-password", delay_between_sends=0)

        assert result["status"] == "partial_success"
        assert result["total_drafts"] == 2
        assert result["sent"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1


def test_missing_credentials():
    """Verify error returned when email or password are missing."""
    result = send_all_drafts(user="", password="")
    assert result["status"] == "failed"
    assert "Missing EMAIL_GMAIL_USER or EMAIL_GMAIL_PASSWORD" in result["errors"][0]["error"]
