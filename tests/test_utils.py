"""Tests for utility functions."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.padel_booker.utils import (
    is_booking_enabled,
    setup_logging,
)


class TestIsBookingEnabled:
    """Tests for is_booking_enabled function."""

    def test_booking_enabled_when_true(self):
        """Test that booking is enabled when ENABLE_BOOKING is 'true'."""
        with patch.dict(os.environ, {"ENABLE_BOOKING": "true"}):
            assert is_booking_enabled() is True

    def test_booking_enabled_when_true_uppercase(self):
        """Test that booking is enabled when ENABLE_BOOKING is 'TRUE'."""
        with patch.dict(os.environ, {"ENABLE_BOOKING": "TRUE"}):
            assert is_booking_enabled() is True

    def test_booking_enabled_when_true_mixed_case(self):
        """Test that booking is enabled when ENABLE_BOOKING is 'True'."""
        with patch.dict(os.environ, {"ENABLE_BOOKING": "True"}):
            assert is_booking_enabled() is True

    def test_booking_disabled_when_false(self):
        """Test that booking is disabled when ENABLE_BOOKING is 'false'."""
        with patch.dict(os.environ, {"ENABLE_BOOKING": "false"}):
            assert is_booking_enabled() is False

    def test_booking_disabled_when_not_set(self):
        """Test that booking is disabled when ENABLE_BOOKING is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove ENABLE_BOOKING if it exists
            os.environ.pop("ENABLE_BOOKING", None)
            assert is_booking_enabled() is False

    def test_booking_disabled_when_other_value(self):
        """Test that booking is disabled when ENABLE_BOOKING is any other value."""
        with patch.dict(os.environ, {"ENABLE_BOOKING": "yes"}):
            assert is_booking_enabled() is False

        with patch.dict(os.environ, {"ENABLE_BOOKING": "1"}):
            assert is_booking_enabled() is False


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_returns_logger(self):
        """Test that setup_logging returns a logger instance."""
        logger = setup_logging("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"

    def test_setup_logging_with_default_name(self):
        """Test that setup_logging works with default name."""
        logger = setup_logging()
        assert logger is not None

    def test_setup_logging_with_custom_name(self):
        """Test that setup_logging works with custom name."""
        logger = setup_logging("custom_name")
        assert logger.name == "custom_name"
