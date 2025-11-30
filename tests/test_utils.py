"""Unit tests for utility functions."""

import pytest
from unittest.mock import Mock, patch

from padel_booker.utils import (
    is_booking_enabled,
    setup_driver,
    setup_logging,
    authenticate_user,
)


@pytest.mark.unit
class TestIsBookingEnabled:
    """Test is_booking_enabled function."""

    def test_enabled_when_env_is_true(self, monkeypatch):
        """Test booking is enabled when ENABLE_BOOKING is 'true'."""
        monkeypatch.setenv("ENABLE_BOOKING", "true")
        assert is_booking_enabled() is True

    def test_enabled_when_env_is_TRUE(self, monkeypatch):
        """Test booking is enabled when ENABLE_BOOKING is 'TRUE' (case insensitive)."""
        monkeypatch.setenv("ENABLE_BOOKING", "TRUE")
        assert is_booking_enabled() is True

    def test_disabled_when_env_is_false(self, monkeypatch):
        """Test booking is disabled when ENABLE_BOOKING is 'false'."""
        monkeypatch.setenv("ENABLE_BOOKING", "false")
        assert is_booking_enabled() is False

    def test_disabled_when_env_is_missing(self, monkeypatch):
        """Test booking is disabled when ENABLE_BOOKING is not set."""
        monkeypatch.delenv("ENABLE_BOOKING", raising=False)
        assert is_booking_enabled() is False

    def test_disabled_when_env_is_other_value(self, monkeypatch):
        """Test booking is disabled for any value other than 'true'."""
        monkeypatch.setenv("ENABLE_BOOKING", "yes")
        assert is_booking_enabled() is False


@pytest.mark.unit
class TestSetupDriver:
    """Test setup_driver function."""

    @patch("padel_booker.utils.webdriver.Chrome")
    @patch("padel_booker.utils.Service")
    @patch("padel_booker.utils.WebDriverWait")
    def test_mobile_mode(self, mock_wait, mock_service, mock_chrome, monkeypatch):
        """Test driver setup in mobile mode."""
        monkeypatch.setenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        mock_driver_instance = Mock()
        mock_chrome.return_value = mock_driver_instance

        driver, wait = setup_driver(device_mode="mobile")

        # Verify mobile emulation was configured
        mock_chrome.assert_called_once()
        call_kwargs = mock_chrome.call_args[1]
        assert "options" in call_kwargs

        # Verify driver and wait were returned
        assert driver == mock_driver_instance
        mock_wait.assert_called_once_with(mock_driver_instance, 10)

    @patch("padel_booker.utils.webdriver.Chrome")
    @patch("padel_booker.utils.Service")
    @patch("padel_booker.utils.WebDriverWait")
    def test_desktop_mode(self, mock_wait, mock_service, mock_chrome, monkeypatch):
        """Test driver setup in desktop mode."""
        monkeypatch.setenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        mock_driver_instance = Mock()
        mock_chrome.return_value = mock_driver_instance

        driver, wait = setup_driver(device_mode="desktop")

        # Verify driver was created
        mock_chrome.assert_called_once()
        assert driver == mock_driver_instance

    def test_invalid_mode_raises_error(self, monkeypatch):
        """Test that invalid device mode raises ValueError."""
        monkeypatch.setenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        with pytest.raises(ValueError, match="Invalid device_mode"):
            setup_driver(device_mode="tablet")

    def test_missing_chromedriver_path_raises_error(self, monkeypatch):
        """Test that missing CHROMEDRIVER_PATH raises RuntimeError."""
        monkeypatch.delenv("CHROMEDRIVER_PATH", raising=False)

        with pytest.raises(RuntimeError, match="CHROMEDRIVER_PATH"):
            setup_driver(device_mode="mobile")

    @patch("padel_booker.utils.webdriver.Chrome")
    @patch("padel_booker.utils.Service")
    @patch("padel_booker.utils.WebDriverWait")
    def test_default_mode_is_mobile(self, mock_wait, mock_service, mock_chrome, monkeypatch):
        """Test that default device mode is mobile."""
        monkeypatch.setenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

        mock_driver_instance = Mock()
        mock_chrome.return_value = mock_driver_instance

        driver, wait = setup_driver()  # No device_mode specified

        # Should succeed (mobile is default)
        assert driver == mock_driver_instance


@pytest.mark.unit
class TestSetupLogging:
    """Test setup_logging function."""

    def test_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_default_logger_name(self):
        """Test that default logger name is used when not provided."""
        logger = setup_logging()
        assert logger.name == "padel_booker.utils"


@pytest.mark.unit
class TestAuthenticateUser:
    """Test authenticate_user function."""

    def test_successful_authentication(self, monkeypatch):
        """Test successful authentication with correct credentials."""
        from fastapi.security import HTTPBasicCredentials

        monkeypatch.setenv("API_USERNAME", "admin")
        monkeypatch.setenv("API_PASSWORD", "secret")

        credentials = HTTPBasicCredentials(username="admin", password="secret")

        result = authenticate_user(credentials)
        assert result is True

    def test_wrong_username(self, monkeypatch):
        """Test authentication fails with wrong username."""
        from fastapi.security import HTTPBasicCredentials
        from fastapi import HTTPException

        monkeypatch.setenv("API_USERNAME", "admin")
        monkeypatch.setenv("API_PASSWORD", "secret")

        credentials = HTTPBasicCredentials(username="wrong", password="secret")

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(credentials)

        assert exc_info.value.status_code == 401

    def test_wrong_password(self, monkeypatch):
        """Test authentication fails with wrong password."""
        from fastapi.security import HTTPBasicCredentials
        from fastapi import HTTPException

        monkeypatch.setenv("API_USERNAME", "admin")
        monkeypatch.setenv("API_PASSWORD", "secret")

        credentials = HTTPBasicCredentials(username="admin", password="wrong")

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(credentials)

        assert exc_info.value.status_code == 401

    def test_missing_api_credentials(self, monkeypatch):
        """Test authentication fails when API credentials are not configured."""
        from fastapi.security import HTTPBasicCredentials
        from fastapi import HTTPException

        monkeypatch.delenv("API_USERNAME", raising=False)
        monkeypatch.delenv("API_PASSWORD", raising=False)

        credentials = HTTPBasicCredentials(username="admin", password="secret")

        with pytest.raises(HTTPException) as exc_info:
            authenticate_user(credentials)

        assert exc_info.value.status_code == 500
