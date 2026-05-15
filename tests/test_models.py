"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from padel_booker.models import BookingRequest, ConditionalSkipRule


@pytest.mark.unit
class TestBookingRequest:
    """Test BookingRequest model."""

    def test_valid_booking_request(self):
        """Test creating a valid booking request."""
        data = {
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe", "Jane Smith"],
        }

        request = BookingRequest(**data)

        assert request.days_offset == 28
        assert request.login_url is None
        assert request.start_time == "21:30"
        assert request.duration_hours == 1.5
        assert request.booker_first_name == "John"
        assert request.player_candidates == ["John Doe", "Jane Smith"]
        assert request.skip_weekends is True
        assert request.skip_dates == []
        assert request.conditional_skip_rules == []

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            BookingRequest()

        errors = exc_info.value.errors()
        field_names = {e["loc"][0] for e in errors}
        assert "start_time" in field_names
        assert "duration_hours" in field_names
        assert "booker_first_name" in field_names
        assert "player_candidates" in field_names

    def test_custom_days_offset(self):
        """Test that days_offset can be set explicitly."""
        data = {
            "days_offset": 14,
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
        }
        request = BookingRequest(**data)
        assert request.days_offset == 14

    def test_login_url_override(self):
        """Test that login_url can be set explicitly in the request."""
        data = {
            "login_url": "https://example.com",
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
        }
        request = BookingRequest(**data)
        assert request.login_url == "https://example.com"

    def test_skip_options(self):
        """Test skip_weekends, skip_dates, and conditional_skip_rules fields."""
        data = {
            "start_time": "21:30",
            "duration_hours": 1.5,
            "booker_first_name": "John",
            "player_candidates": ["John Doe"],
            "skip_weekends": False,
            "skip_dates": ["2025-12-25"],
            "conditional_skip_rules": [{"weekday": 3, "before_date": "2026-01-01"}],
        }
        request = BookingRequest(**data)
        assert request.skip_weekends is False
        assert request.skip_dates == ["2025-12-25"]
        assert len(request.conditional_skip_rules) == 1
        assert request.conditional_skip_rules[0].weekday == 3


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
