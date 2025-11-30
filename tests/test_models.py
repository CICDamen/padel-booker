"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from src.padel_booker.models import BookingRequest, ConfigModel


class TestBookingRequest:
    """Tests for BookingRequest model."""

    def test_valid_booking_request(self):
        """Test that a valid booking request is created successfully."""
        request = BookingRequest(
            login_url="https://example.com/",
            booking_date="2025-07-28",
            start_time="21:30",
            duration_hours=1.5,
            booker_first_name="John",
            player_candidates=["John Smith", "Jane Doe", "Mike Johnson"],
        )
        assert request.login_url == "https://example.com/"
        assert request.booking_date == "2025-07-28"
        assert request.start_time == "21:30"
        assert request.duration_hours == 1.5
        assert request.booker_first_name == "John"
        assert request.player_candidates == ["John Smith", "Jane Doe", "Mike Johnson"]

    def test_booking_request_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            BookingRequest(
                login_url="https://example.com/",
                booking_date="2025-07-28",
                # Missing start_time and other required fields
            )

    def test_booking_request_empty_player_candidates(self):
        """Test that empty player_candidates list is valid."""
        request = BookingRequest(
            login_url="https://example.com/",
            booking_date="2025-07-28",
            start_time="21:30",
            duration_hours=1.5,
            booker_first_name="John",
            player_candidates=[],
        )
        assert request.player_candidates == []

    def test_booking_request_duration_as_integer(self):
        """Test that integer duration is converted to float."""
        request = BookingRequest(
            login_url="https://example.com/",
            booking_date="2025-07-28",
            start_time="21:30",
            duration_hours=2,
            booker_first_name="John",
            player_candidates=["Player 1"],
        )
        assert request.duration_hours == 2.0


class TestConfigModel:
    """Tests for ConfigModel model."""

    def test_valid_config_model(self):
        """Test that a valid config model is created successfully."""
        config = ConfigModel(
            login_url="https://example.com/",
            booking_date="2025-07-28",
            start_time="21:30",
            duration_hours=1.5,
        )
        assert config.login_url == "https://example.com/"
        assert config.booking_date == "2025-07-28"
        assert config.start_time == "21:30"
        assert config.duration_hours == 1.5

    def test_config_model_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            ConfigModel(
                login_url="https://example.com/",
                # Missing other required fields
            )
