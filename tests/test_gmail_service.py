"""
Unit tests for Gmail API draft sending, pagination, and error resilience.
All Gmail API calls are strictly mocked. No real emails are sent.
"""

from unittest.mock import MagicMock, patch
import pytest

from gmail_service import (
    send_all_drafts,
    get_gmail_client,
    MissingCredentialsError
)
from googleapiclient.errors import HttpError
from httplib2 import Response


def test_no_drafts_found():
    """Test 5: Zero drafts found in account."""
    mock_service = MagicMock()
    # Mock drafts().list().execute() returning no drafts
    mock_service.users().drafts().list().execute.return_value = {"drafts": []}

    result = send_all_drafts(service=mock_service, delay_between_sends=0)

    assert result["status"] == "completed"
    assert result["total_drafts"] == 0
    assert result["sent"] == 0
    assert result["failed"] == 0
    assert "No drafts found" in result["message"]
    mock_service.users().drafts().send().execute.assert_not_called()


def test_multiple_drafts_with_pagination():
    """Test 6: Multiple drafts with pagination (2 pages)."""
    mock_service = MagicMock()

    # Page 1 returns 2 drafts and a nextPageToken
    # Page 2 returns 1 draft and no nextPageToken
    list_mock = mock_service.users().drafts().list

    def mock_list_side_effect(**kwargs):
        page_token = kwargs.get("pageToken")
        mock_req = MagicMock()
        if not page_token:
            mock_req.execute.return_value = {
                "drafts": [{"id": "draft_1"}, {"id": "draft_2"}],
                "nextPageToken": "page_2_token"
            }
        else:
            mock_req.execute.return_value = {
                "drafts": [{"id": "draft_3"}]
            }
        return mock_req

    list_mock.side_effect = mock_list_side_effect

    # Mock send().execute() success
    mock_service.users().drafts().send().execute.return_value = {"id": "msg_sent"}

    # Mock get() for metadata logging
    mock_service.users().drafts().get().execute.return_value = {
        "message": {"payload": {"headers": [{"name": "Subject", "value": "Test Subject"}]}}
    }

    result = send_all_drafts(service=mock_service, delay_between_sends=0)

    assert result["status"] == "completed"
    assert result["total_drafts"] == 3
    assert result["sent"] == 3
    assert result["failed"] == 0
    assert len(result["errors"]) == 0


def test_one_draft_fails_others_succeed():
    """Test 7: One draft fails (HTTP 500 error), other drafts succeed."""
    mock_service = MagicMock()

    mock_service.users().drafts().list().execute.return_value = {
        "drafts": [{"id": "draft_success_1"}, {"id": "draft_failed"}, {"id": "draft_success_2"}]
    }

    # Setup side effect for send().execute()
    http_error_resp = Response({"status": 500, "reason": "Internal Server Error"})
    http_error = HttpError(resp=http_error_resp, content=b"Server error sending draft")

    def mock_send_side_effect(**kwargs):
        draft_id = kwargs.get("body", {}).get("id")
        mock_req = MagicMock()
        if draft_id == "draft_failed":
            mock_req.execute.side_effect = http_error
        else:
            mock_req.execute.return_value = {"id": f"msg_{draft_id}"}
        return mock_req

    mock_service.users().drafts().send.side_effect = mock_send_side_effect

    result = send_all_drafts(service=mock_service, delay_between_sends=0)

    assert result["status"] == "partial_success"
    assert result["total_drafts"] == 3
    assert result["sent"] == 2
    assert result["failed"] == 1
    assert len(result["errors"]) == 1
    assert result["errors"][0]["draft_id"] == "draft_failed"


def test_oauth_credential_construction_from_refresh_token():
    """Test 10: OAuth credential construction using a refresh token."""
    with patch("gmail_service.Credentials") as mock_creds_cls, \
         patch("gmail_service.build") as mock_build:

        mock_creds_instance = MagicMock()
        mock_creds_cls.return_value = mock_creds_instance

        service = get_gmail_client(
            client_id="test-client-id",
            client_secret="test-client-secret",
            refresh_token="test-refresh-token"
        )

        mock_creds_cls.assert_called_once_with(
            token=None,
            refresh_token="test-refresh-token",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="test-client-id",
            client_secret="test-client-secret",
            scopes=["https://www.googleapis.com/auth/gmail.compose"]
        )
        mock_creds_instance.refresh.assert_called_once()
        mock_build.assert_called_once()
