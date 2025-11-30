"""Unit tests for custom exceptions."""

import pytest

from padel_booker.exceptions import (
    LoginFailedError,
    SlotNotFoundError,
    BookingFailedError,
    PlayerSelectionExhaustedError,
)


@pytest.mark.unit
class TestCustomExceptions:
    """Test custom exception classes."""

    def test_login_failed_error(self):
        """Test LoginFailedError can be raised and caught."""
        with pytest.raises(LoginFailedError) as exc_info:
            raise LoginFailedError("Invalid credentials")

        assert "Invalid credentials" in str(exc_info.value)
        assert isinstance(exc_info.value, Exception)

    def test_slot_not_found_error(self):
        """Test SlotNotFoundError can be raised and caught."""
        with pytest.raises(SlotNotFoundError) as exc_info:
            raise SlotNotFoundError("No slots available")

        assert "No slots available" in str(exc_info.value)
        assert isinstance(exc_info.value, Exception)

    def test_booking_failed_error(self):
        """Test BookingFailedError can be raised and caught."""
        with pytest.raises(BookingFailedError) as exc_info:
            raise BookingFailedError("Payment declined")

        assert "Payment declined" in str(exc_info.value)
        assert isinstance(exc_info.value, Exception)

    def test_player_selection_exhausted_error(self):
        """Test PlayerSelectionExhaustedError can be raised and caught."""
        with pytest.raises(PlayerSelectionExhaustedError) as exc_info:
            raise PlayerSelectionExhaustedError("All players blocked")

        assert "All players blocked" in str(exc_info.value)
        assert isinstance(exc_info.value, Exception)

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from Exception."""
        assert issubclass(LoginFailedError, Exception)
        assert issubclass(SlotNotFoundError, Exception)
        assert issubclass(BookingFailedError, Exception)
        assert issubclass(PlayerSelectionExhaustedError, Exception)

    def test_exceptions_without_message(self):
        """Test that exceptions can be raised without message."""
        with pytest.raises(LoginFailedError):
            raise LoginFailedError()

        with pytest.raises(SlotNotFoundError):
            raise SlotNotFoundError()

        with pytest.raises(BookingFailedError):
            raise BookingFailedError()

        with pytest.raises(PlayerSelectionExhaustedError):
            raise PlayerSelectionExhaustedError()
