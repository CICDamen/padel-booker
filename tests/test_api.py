"""Tests for FastAPI endpoints."""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import base64

from src.padel_booker.api import app


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_check(self):
        """Test that health check returns healthy status."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "padel-booker"}


class TestAuthenticationEndpoints:
    """Tests for endpoints requiring authentication."""

    def test_status_without_auth(self):
        """Test that /api/status returns 401 without authentication."""
        client = TestClient(app)
        response = client.get("/api/status")
        assert response.status_code == 401

    def test_book_without_auth(self):
        """Test that /api/book returns 401 without authentication."""
        client = TestClient(app)
        response = client.post("/api/book", json={})
        assert response.status_code == 401

    @patch.dict(os.environ, {"API_USERNAME": "testuser", "API_PASSWORD": "testpass"})
    def test_status_with_valid_auth(self):
        """Test that /api/status returns 200 with valid authentication."""
        client = TestClient(app)
        credentials = base64.b64encode(b"testuser:testpass").decode("utf-8")
        response = client.get(
            "/api/status",
            headers={"Authorization": f"Basic {credentials}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        assert "result" in data
        assert "started_at" in data

    @patch.dict(os.environ, {"API_USERNAME": "testuser", "API_PASSWORD": "testpass"})
    def test_status_with_invalid_auth(self):
        """Test that /api/status returns 401 with invalid authentication."""
        client = TestClient(app)
        credentials = base64.b64encode(b"wronguser:wrongpass").decode("utf-8")
        response = client.get(
            "/api/status",
            headers={"Authorization": f"Basic {credentials}"}
        )
        assert response.status_code == 401


class TestBookEndpoint:
    """Tests for the /api/book endpoint."""

    @patch.dict(os.environ, {
        "API_USERNAME": "testuser",
        "API_PASSWORD": "testpass",
        "BOOKER_USERNAME": "booker",
        "BOOKER_PASSWORD": "bookerpass"
    })
    @patch("src.padel_booker.api.threading.Thread")
    def test_book_starts_booking_process(self, mock_thread):
        """Test that /api/book starts the booking process."""
        # Reset booking status before test
        from src.padel_booker.api import booking_status
        booking_status["running"] = False
        booking_status["result"] = None
        booking_status["started_at"] = None

        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        client = TestClient(app)
        credentials = base64.b64encode(b"testuser:testpass").decode("utf-8")
        response = client.post(
            "/api/book",
            headers={"Authorization": f"Basic {credentials}"},
            json={
                "login_url": "https://example.com/",
                "booking_date": "2025-07-28",
                "start_time": "21:30",
                "duration_hours": 1.5,
                "booker_first_name": "John",
                "player_candidates": ["Player 1", "Player 2", "Player 3"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["message"] == "Booking process started"
        mock_thread_instance.start.assert_called_once()

    @patch.dict(os.environ, {
        "API_USERNAME": "testuser",
        "API_PASSWORD": "testpass"
    })
    def test_book_without_booker_credentials(self):
        """Test that /api/book returns 500 when booker credentials are missing."""
        # Remove BOOKER_* env vars if they exist
        os.environ.pop("BOOKER_USERNAME", None)
        os.environ.pop("BOOKER_PASSWORD", None)

        # Reset booking status before test
        from src.padel_booker.api import booking_status
        booking_status["running"] = False
        booking_status["result"] = None
        booking_status["started_at"] = None

        client = TestClient(app)
        credentials = base64.b64encode(b"testuser:testpass").decode("utf-8")
        response = client.post(
            "/api/book",
            headers={"Authorization": f"Basic {credentials}"},
            json={
                "login_url": "https://example.com/",
                "booking_date": "2025-07-28",
                "start_time": "21:30",
                "duration_hours": 1.5,
                "booker_first_name": "John",
                "player_candidates": ["Player 1", "Player 2", "Player 3"]
            }
        )
        assert response.status_code == 500

    @patch.dict(os.environ, {
        "API_USERNAME": "testuser",
        "API_PASSWORD": "testpass",
        "BOOKER_USERNAME": "booker",
        "BOOKER_PASSWORD": "bookerpass"
    })
    def test_book_with_invalid_request_body(self):
        """Test that /api/book returns 422 with invalid request body."""
        client = TestClient(app)
        credentials = base64.b64encode(b"testuser:testpass").decode("utf-8")
        response = client.post(
            "/api/book",
            headers={"Authorization": f"Basic {credentials}"},
            json={
                "login_url": "https://example.com/",
                # Missing required fields
            }
        )
        assert response.status_code == 422
