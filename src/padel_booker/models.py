"""Pydantic models for the Padel Booker API."""

from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List, Optional


class ConditionalSkipRule(BaseModel):
    """Rule to skip a specific weekday within an optional date range.

    Example: skip Thursday (weekday=3) before 2026-01-01:
        ConditionalSkipRule(weekday=3, before_date="2026-01-01")
    """
    weekday: int  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    before_date: Optional[str] = None  # Skip this weekday if date < before_date
    after_date: Optional[str] = None  # Skip this weekday if date >= after_date


class BookingRequest(BaseModel):
    login_url: str
    booking_date: str = Field(
        default_factory=lambda: (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    start_time: str
    duration_hours: float
    booker_first_name: str
    player_candidates: List[str]
    skip_dates: List[str] = Field(default_factory=list)
    skip_weekends: bool = True
    conditional_skip_rules: List[ConditionalSkipRule] = Field(default_factory=list)


class ConfigModel(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float
