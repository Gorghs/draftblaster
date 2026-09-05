"""
Unit tests for send_drafts.py standalone CLI entry point.
"""

from unittest.mock import patch, MagicMock
import pytest
import sys

from send_drafts import main, mask_email


def test_mask_email():
    """Verify email masking hides local part for safe logging."""
    assert mask_email("karthick@gmail.com") == "ka******@gmail.com"
    assert mask_email("ab@domain.com") == "a*@domain.com"
    assert mask_email("a@b.com") == "a*@b.com"
    assert mask_email("") == "***"
    assert mask_email("invalid") == "***"


def test_cli_missing_credentials(monkeypatch):
    """Verify CLI exits with code 1 when credentials are missing."""
    monkeypatch.setenv("EMAIL_GMAIL_USER", "")
    monkeypatch.setenv("EMAIL_GMAIL_PASSWORD", "")

    test_args = ["send_drafts.py"]
    with patch.object(sys, "argv", test_args):
        exit_code = main()
        assert exit_code == 1


def test_cli_dry_run_success(monkeypatch):
    """Verify CLI dry run executes without connecting to SMTP or deleting drafts."""
    monkeypatch.setenv("EMAIL_GMAIL_USER", "test@gmail.com")
    monkeypatch.setenv("EMAIL_GMAIL_PASSWORD", "apppassword123")

    mock_imap = MagicMock()
    mock_imap.list.return_value = ("OK", [b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"'])
    mock_imap.select.return_value = ("OK", [b"1"])
    mock_imap.search.return_value = ("OK", [b"1"])
    mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {50})", b"To: a@b.com\r\nSubject: Test\r\n\r\nHi")])

    with patch("imaplib.IMAP4_SSL", return_value=mock_imap), \
         patch("smtplib.SMTP") as mock_smtp, \
         patch.object(sys, "argv", ["send_drafts.py", "--dry-run"]):
        exit_code = main()
        assert exit_code == 0
        mock_smtp.assert_not_called()
        mock_imap.store.assert_not_called()


def test_cli_live_send_success(monkeypatch):
    """Verify CLI live run sends drafts and exits with code 0."""
    monkeypatch.setenv("EMAIL_GMAIL_USER", "test@gmail.com")
    monkeypatch.setenv("EMAIL_GMAIL_PASSWORD", "apppassword123")

    mock_imap = MagicMock()
    mock_imap.list.return_value = ("OK", [b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"'])
    mock_imap.select.return_value = ("OK", [b"1"])
    mock_imap.search.return_value = ("OK", [b"1"])
    mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {50})", b"To: a@b.com\r\nSubject: Test\r\n\r\nHi")])

    mock_smtp = MagicMock()

    with patch("imaplib.IMAP4_SSL", return_value=mock_imap), \
         patch("smtplib.SMTP", return_value=mock_smtp), \
         patch.object(sys, "argv", ["send_drafts.py"]):
        exit_code = main()
        assert exit_code == 0
        mock_smtp.send_message.assert_called_once()
        mock_imap.store.assert_called_once()


def test_cli_live_send_failure(monkeypatch):
    """Verify CLI exits with code 1 when all drafts fail to send."""
    monkeypatch.setenv("EMAIL_GMAIL_USER", "test@gmail.com")
    monkeypatch.setenv("EMAIL_GMAIL_PASSWORD", "apppassword123")

    mock_imap = MagicMock()
    mock_imap.list.return_value = ("OK", [b'(\\HasNoChildren \\Drafts) "/" "[Gmail]/Drafts"'])
    mock_imap.select.return_value = ("OK", [b"1"])
    mock_imap.search.return_value = ("OK", [b"1"])
    mock_imap.fetch.return_value = ("OK", [(b"1 (RFC822 {50})", b"To: a@b.com\r\nSubject: Test\r\n\r\nHi")])

    mock_smtp = MagicMock()
    mock_smtp.send_message.side_effect = Exception("Connection lost")

    with patch("imaplib.IMAP4_SSL", return_value=mock_imap), \
         patch("smtplib.SMTP", return_value=mock_smtp), \
         patch.object(sys, "argv", ["send_drafts.py"]):
        exit_code = main()
        assert exit_code == 1
