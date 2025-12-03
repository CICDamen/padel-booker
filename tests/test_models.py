"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from padel_booker.models import BookingRequest, ConfigModel


@pytest.mark.unit
class TestBookingRequest:
    """Test BookingRequest model."""

    def test_valid_booking_request(self):
        """Test creating a valid booking request."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe", "Jane Smith"],
        }

        request = BookingRequest(**data)

        assert request.login_url == "https://example.com"
        assert request.booking_date == "2025-12-01"
        assert request.start_time == "21:30"
        assert request.duration_hours == 1.5
        assert request.booker_first_name == "John"
        assert request.player_candidates == ["John Doe", "Jane Smith"]

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        data = {
            "login_url": "https://example.com",
            # Missing other required fields
        }

        with pytest.raises(ValidationError) as exc_info:
            BookingRequest(**data)

        errors = exc_info.value.errors()
        assert len(errors) >= 5  # At least 5 missing required fields

    def test_empty_player_candidates(self):
        """Test booking request with empty player candidates list."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": [],  # Empty list is valid
        }

        request = BookingRequest(**data)
        assert request.player_candidates == []

    def test_float_duration_hours(self):
        """Test that duration_hours accepts float values."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 2.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
        }

        request = BookingRequest(**data)
        assert request.duration_hours == 2.5

    def test_integer_duration_hours(self):
        """Test that duration_hours accepts integer values."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 2,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
        }

        request = BookingRequest(**data)
        assert request.duration_hours == 2.0


@pytest.mark.unit
class TestConfigModel:
    """Test ConfigModel."""

    def test_valid_config(self):
        """Test creating a valid config model."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 1.5,
        }

        config = ConfigModel(**data)

        assert config.login_url == "https://example.com"
        assert config.booking_date == "2025-12-01"
        assert config.start_time == "21:30"
        assert config.duration_hours == 1.5

    def test_missing_required_fields_in_config(self):
        """Test that ConfigModel requires all fields."""
        data = {
            "login_url": "https://example.com",
            # Missing other required fields
        }

        with pytest.raises(ValidationError):
            ConfigModel(**data)
