"""
API integration tests for FastAPI endpoints: /health, /trigger, and security verification.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import pytest

from main import app
from gmail_service import send_all_drafts

client = TestClient(app)


def test_health_endpoint():
    """Test standard health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "gmail-draft-auto-sender"


def test_dashboard_endpoint():
    """Test dashboard endpoint renders HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Gmail Draft Auto-Sender" in response.text


def test_trigger_secret_validation():
    """Test 8: Trigger secret validation (query parameter and header)."""
    with patch("main.TRIGGER_SECRET", "my_super_secret_token"):
        # 1. Missing secret -> 401
        res_missing = client.get("/trigger")
        assert res_missing.status_code == 401

        # 2. Invalid secret -> 401
        res_invalid = client.get("/trigger?secret=wrong_token")
        assert res_invalid.status_code == 401

        # 3. Valid secret via query param -> 200
        with patch("main.evaluate_and_trigger", return_value={"status": "idle"}):
            res_valid_param = client.get("/trigger?secret=my_super_secret_token")
            assert res_valid_param.status_code == 200
            assert res_valid_param.json()["status"] == "idle"

        # 4. Valid secret via header x-trigger-secret -> 200
        with patch("main.evaluate_and_trigger", return_value={"status": "idle"}):
            res_valid_header = client.get("/trigger", headers={"x-trigger-secret": "my_super_secret_token"})
            assert res_valid_header.status_code == 200

        # 5. Valid secret via Authorization: Bearer <token> -> 200
        with patch("main.evaluate_and_trigger", return_value={"status": "idle"}):
            res_valid_bearer = client.get("/trigger", headers={"Authorization": "Bearer my_super_secret_token"})
            assert res_valid_bearer.status_code == 200


def test_missing_environment_variables():
    """Test: Missing environment variables error handling."""
    with patch("gmail_service.EMAIL_GMAIL_USER", ""), \
         patch("gmail_service.EMAIL_GMAIL_PASSWORD", ""):
        result = send_all_drafts(user="", password="")
        assert result["status"] == "failed"
        assert "Missing EMAIL_GMAIL_USER or EMAIL_GMAIL_PASSWORD" in result["errors"][0]["error"]

