"""Exceptions in padel booker flow"""


class LoginFailedError(Exception):
    """Raised when login to the booking system fails."""


class SlotNotFoundError(Exception):
    """Raised when no suitable slot is found for booking."""


class BookingFailedError(Exception):
    """Raised when booking could not be completed."""


class PlayerSelectionExhaustedError(Exception):
    """Raised when all possible player combinations have been tried without success."""
