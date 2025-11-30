"""Tests for custom exceptions."""

import pytest

from src.padel_booker.exceptions import (
    LoginFailedError,
    SlotNotFoundError,
    BookingFailedError,
    PlayerSelectionExhaustedError,
)


class TestExceptions:
    """Tests for custom exception classes."""

    def test_login_failed_error(self):
        """Test LoginFailedError can be raised with message."""
        with pytest.raises(LoginFailedError) as exc_info:
            raise LoginFailedError("Invalid credentials")
        assert str(exc_info.value) == "Invalid credentials"

    def test_login_failed_error_no_message(self):
        """Test LoginFailedError can be raised without message."""
        with pytest.raises(LoginFailedError):
            raise LoginFailedError()

    def test_slot_not_found_error(self):
        """Test SlotNotFoundError can be raised with message."""
        with pytest.raises(SlotNotFoundError) as exc_info:
            raise SlotNotFoundError("No slots available for 21:30")
        assert str(exc_info.value) == "No slots available for 21:30"

    def test_slot_not_found_error_no_message(self):
        """Test SlotNotFoundError can be raised without message."""
        with pytest.raises(SlotNotFoundError):
            raise SlotNotFoundError()

    def test_booking_failed_error(self):
        """Test BookingFailedError can be raised with message."""
        with pytest.raises(BookingFailedError) as exc_info:
            raise BookingFailedError("Booking confirmation failed")
        assert str(exc_info.value) == "Booking confirmation failed"

    def test_booking_failed_error_no_message(self):
        """Test BookingFailedError can be raised without message."""
        with pytest.raises(BookingFailedError):
            raise BookingFailedError()

    def test_player_selection_exhausted_error(self):
        """Test PlayerSelectionExhaustedError can be raised with message."""
        with pytest.raises(PlayerSelectionExhaustedError) as exc_info:
            raise PlayerSelectionExhaustedError("All players blocked")
        assert str(exc_info.value) == "All players blocked"

    def test_player_selection_exhausted_error_no_message(self):
        """Test PlayerSelectionExhaustedError can be raised without message."""
        with pytest.raises(PlayerSelectionExhaustedError):
            raise PlayerSelectionExhaustedError()

    def test_exceptions_inherit_from_exception(self):
        """Test that all custom exceptions inherit from Exception."""
        assert issubclass(LoginFailedError, Exception)
        assert issubclass(SlotNotFoundError, Exception)
        assert issubclass(BookingFailedError, Exception)
        assert issubclass(PlayerSelectionExhaustedError, Exception)
