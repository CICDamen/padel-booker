"""Unit tests for FastAPI endpoints."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from padel_booker.api import app


@pytest.fixture
def client():
    """Fixture providing FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_env(monkeypatch):
    """Fixture providing mocked environment variables."""
    monkeypatch.setenv("API_USERNAME", "admin")
    monkeypatch.setenv("API_PASSWORD", "secret")
    monkeypatch.setenv("BOOKER_USERNAME", "test_user")
    monkeypatch.setenv("BOOKER_PASSWORD", "test_pass")
    monkeypatch.setenv("BOOKING_LOGIN_URL", "https://example.com")


MINIMAL_REQUEST = {
    "start_time": "21:30",
    "duration_hours": 1.5,
    "booker_first_name": "John",
    "player_candidates": ["John Doe"],
}


@pytest.mark.unit
class TestHealthEndpoint:
    """Test /health endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "padel-booker"


@pytest.mark.unit
class TestBookingEndpoint:
    """Test /api/book endpoint."""

    def test_book_without_auth(self, client, mock_env):
        """Test booking endpoint requires authentication."""
        response = client.post("/api/book", json=MINIMAL_REQUEST)

        assert response.status_code == 401

    @patch("padel_booker.api.threading.Thread")
    def test_book_with_auth(self, mock_thread, client, mock_env):
        """Test booking endpoint with valid authentication."""
        response = client.post(
            "/api/book",
            json=MINIMAL_REQUEST,
            auth=("admin", "secret"),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert "started_at" in data
        assert "booking_date" in data

    @patch("padel_booker.api.threading.Thread")
    def test_login_url_in_request_overrides_env(self, mock_thread, client, mock_env):
        """Test that login_url in request body takes precedence over env var."""
        response = client.post(
            "/api/book",
            json={**MINIMAL_REQUEST, "login_url": "https://override.example.com"},
            auth=("admin", "secret"),
        )

        assert response.status_code == 200

    def test_book_missing_login_url_no_env(self, client, monkeypatch):
        """Test booking fails when login_url absent from both request and env var."""
        monkeypatch.setenv("API_USERNAME", "admin")
        monkeypatch.setenv("API_PASSWORD", "secret")
        monkeypatch.setenv("BOOKER_USERNAME", "test_user")
        monkeypatch.setenv("BOOKER_PASSWORD", "test_pass")
        monkeypatch.delenv("BOOKING_LOGIN_URL", raising=False)

        response = client.post(
            "/api/book",
            json=MINIMAL_REQUEST,
            auth=("admin", "secret"),
        )

        assert response.status_code == 400
        assert "login_url" in response.json()["detail"]

    def test_book_with_wrong_credentials(self, client, mock_env):
        """Test booking with wrong credentials."""
        response = client.post(
            "/api/book",
            json=MINIMAL_REQUEST,
            auth=("wrong", "credentials"),
        )

        assert response.status_code == 401

    @patch("padel_booker.api.threading.Thread")
    def test_book_while_booking_running(self, mock_thread, client, mock_env):
        """Test that concurrent bookings are rejected."""
        client.post("/api/book", json=MINIMAL_REQUEST, auth=("admin", "secret"))

        with patch("padel_booker.api.booking_status", {"running": True, "result": None, "started_at": None}):
            response = client.post("/api/book", json=MINIMAL_REQUEST, auth=("admin", "secret"))

        assert response.status_code == 400
        assert "already in progress" in response.json()["detail"]

    def test_book_without_env_credentials(self, client, monkeypatch):
        """Test booking fails when BOOKER credentials are not set."""
        monkeypatch.setenv("API_USERNAME", "admin")
        monkeypatch.setenv("API_PASSWORD", "secret")
        monkeypatch.delenv("BOOKER_USERNAME", raising=False)
        monkeypatch.delenv("BOOKER_PASSWORD", raising=False)

        response = client.post(
            "/api/book",
            json=MINIMAL_REQUEST,
            auth=("admin", "secret"),
        )

        assert response.status_code == 500

    @patch("padel_booker.api.threading.Thread")
    def test_days_offset_computes_booking_date(self, mock_thread, client, mock_env):
        """Test that days_offset is converted to a booking_date in the response."""
        response = client.post(
            "/api/book",
            json={**MINIMAL_REQUEST, "days_offset": 7},
            auth=("admin", "secret"),
        )

        assert response.status_code == 200
        from datetime import datetime, timedelta
        expected = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        assert response.json()["booking_date"] == expected


@pytest.mark.unit
class TestStatusEndpoint:
    """Test /api/status endpoint."""

    def test_status_without_auth(self, client, mock_env):
        """Test status endpoint requires authentication."""
        response = client.get("/api/status")

        assert response.status_code == 401

    def test_status_with_auth(self, client, mock_env):
        """Test status endpoint with valid authentication."""
        response = client.get("/api/status", auth=("admin", "secret"))

        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        assert "result" in data
        assert "started_at" in data

    def test_status_initial_state(self, client, mock_env):
        """Test status endpoint returns initial state."""
        response = client.get("/api/status", auth=("admin", "secret"))

        assert response.status_code == 200
        data = response.json()
        assert data["running"] is False
        assert data["result"] is None

    @patch("padel_booker.api.booking_status")
    def test_status_while_running(self, mock_status, client, mock_env):
        """Test status endpoint while booking is running."""
        mock_status.__getitem__.side_effect = lambda k: {
            "running": True,
            "result": None,
            "started_at": "2025-01-01T00:00:00"
        }[k]

        response = client.get("/api/status", auth=("admin", "secret"))

        assert response.status_code == 200
        data = response.json()
        assert data["running"] is True

    def test_status_with_wrong_credentials(self, client, mock_env):
        """Test status with wrong credentials."""
        response = client.get("/api/status", auth=("wrong", "credentials"))

        assert response.status_code == 401
