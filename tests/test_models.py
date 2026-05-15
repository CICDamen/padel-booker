"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from padel_booker.models import BookingRequest, ConfigModel, ConditionalSkipRule


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
        assert len(errors) >= 4  # booking_date is optional; at least 4 missing required fields

    def test_default_booking_date_is_30_days_from_now(self):
        """Test that booking_date defaults to today + 30 days when not provided."""
        from datetime import datetime, timedelta
        from unittest.mock import patch

        fixed_now = datetime(2026, 1, 1, 12, 0, 0)
        expected_date = (fixed_now + timedelta(days=30)).strftime("%Y-%m-%d")

        data = {
            "login_url": "https://example.com",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
        }

        with patch("padel_booker.models.datetime") as mock_dt:
            mock_dt.now.return_value = fixed_now
            request = BookingRequest(**data)

        assert request.booking_date == expected_date

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
class TestBookingRequestSkipOptions:
    """Test skip_dates, skip_weekends, and conditional_skip_rules fields."""

    def test_skip_dates_defaults_to_empty(self):
        """Test skip_dates defaults to empty list."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
        }
        request = BookingRequest(**data)
        assert request.skip_dates == []
        assert request.skip_weekends is True
        assert request.conditional_skip_rules == []

    def test_skip_dates_with_specific_dates(self):
        """Test skip_dates accepts a list of date strings."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
            "skip_dates": ["2025-12-24", "2025-12-25"],
            "skip_weekends": False,
        }
        request = BookingRequest(**data)
        assert request.skip_dates == ["2025-12-24", "2025-12-25"]
        assert request.skip_weekends is False

    def test_conditional_skip_rule_model(self):
        """Test ConditionalSkipRule model validation."""
        rule = ConditionalSkipRule(weekday=3, before_date="2026-01-01")
        assert rule.weekday == 3
        assert rule.before_date == "2026-01-01"
        assert rule.after_date is None

    def test_conditional_skip_rules_in_booking_request(self):
        """Test conditional_skip_rules field in BookingRequest."""
        data = {
            "login_url": "https://example.com",
            "booking_date": "2025-12-01",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
            "conditional_skip_rules": [
                {"weekday": 3, "before_date": "2026-01-01"},
            ],
        }
        request = BookingRequest(**data)
        assert len(request.conditional_skip_rules) == 1
        assert request.conditional_skip_rules[0].weekday == 3
        assert request.conditional_skip_rules[0].before_date == "2026-01-01"


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
