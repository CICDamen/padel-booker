"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from padel_booker.models import BookingRequest, BookingConfig, ConditionalSkipRule


@pytest.mark.unit
class TestBookingRequest:
    """Test BookingRequest model."""

    def test_valid_booking_request(self):
        """Test creating a valid booking request."""
        data = {
            "booking_date": "2025-12-01",
            "booker_first_name": "John",
            "player_candidates": ["John Doe", "Jane Smith"],
        }

        request = BookingRequest(**data)

        assert request.booking_date == "2025-12-01"
        assert request.booker_first_name == "John"
        assert request.player_candidates == ["John Doe", "Jane Smith"]

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BookingRequest()  # Missing booker_first_name and player_candidates

        errors = exc_info.value.errors()
        assert len(errors) == 2

    def test_default_booking_date_is_30_days_from_now(self):
        """Test that booking_date defaults to today + 30 days when not provided."""
        from datetime import datetime, timedelta
        from unittest.mock import patch

        fixed_now = datetime(2026, 1, 1, 12, 0, 0)
        expected_date = (fixed_now + timedelta(days=30)).strftime("%Y-%m-%d")

        data = {
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
            "booking_date": "2025-12-01",
            "booker_first_name": "John",
            "player_candidates": [],
        }

        request = BookingRequest(**data)
        assert request.player_candidates == []


@pytest.mark.unit
class TestBookingConfig:
    """Test BookingConfig model."""

    def test_valid_config(self):
        """Test creating a valid booking config."""
        data = {
            "login_url": "https://example.com",
            "start_time": "21:30",
            "duration_hours": 1.5,
        }

        config = BookingConfig(**data)

        assert config.login_url == "https://example.com"
        assert config.start_time == "21:30"
        assert config.duration_hours == 1.5
        assert config.skip_weekends is True
        assert config.skip_dates == []
        assert config.conditional_skip_rules == []

    def test_missing_required_fields(self):
        """Test that BookingConfig requires all mandatory fields."""
        with pytest.raises(ValidationError):
            BookingConfig(login_url="https://example.com")

    def test_skip_options_in_config(self):
        """Test that skip options can be set in config."""
        data = {
            "login_url": "https://example.com",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "skip_weekends": False,
            "skip_dates": ["2025-12-25"],
            "conditional_skip_rules": [{"weekday": 3, "before_date": "2026-01-01"}],
        }

        config = BookingConfig(**data)

        assert config.skip_weekends is False
        assert config.skip_dates == ["2025-12-25"]
        assert len(config.conditional_skip_rules) == 1
        assert config.conditional_skip_rules[0].weekday == 3


@pytest.mark.unit
class TestConditionalSkipRule:
    """Test ConditionalSkipRule model."""

    def test_weekday_only_no_date_range(self):
        """Test rule with only weekday (unconditional skip)."""
        rule = ConditionalSkipRule(weekday=3)
        assert rule.weekday == 3
        assert rule.before_date is None
        assert rule.after_date is None

    def test_before_date(self):
        """Test rule with before_date."""
        rule = ConditionalSkipRule(weekday=3, before_date="2026-01-01")
        assert rule.before_date == "2026-01-01"
        assert rule.after_date is None

    def test_after_date(self):
        """Test rule with after_date."""
        rule = ConditionalSkipRule(weekday=1, after_date="2026-06-01")
        assert rule.after_date == "2026-06-01"

    def test_both_dates(self):
        """Test rule with both before_date and after_date."""
        rule = ConditionalSkipRule(weekday=0, before_date="2025-01-01", after_date="2026-01-01")
        assert rule.before_date == "2025-01-01"
        assert rule.after_date == "2026-01-01"
