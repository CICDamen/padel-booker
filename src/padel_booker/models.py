"""Pydantic models for the Padel Booker API."""

from pydantic import BaseModel, Field
from typing import List, Optional


class ConditionalSkipRule(BaseModel):
    """Rule to skip a specific weekday, optionally limited to a date range.

    - No date conditions → always skip this weekday.
      Example: {"weekday": 3}  # skip Thursday forever
    - before_date only → skip this weekday only before that date.
      Example: {"weekday": 3, "before_date": "2026-01-01"}
    - after_date only → skip this weekday on and after that date.
    - Both → skip this weekday within that window.

    weekday: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
    """
    weekday: int
    before_date: Optional[str] = None
    after_date: Optional[str] = None


class BookingRequest(BaseModel):
    days_offset: int = Field(default=28, ge=0, description="Days from today to target booking date")
    login_url: Optional[str] = Field(default=None, description="Booking platform URL. Falls back to BOOKING_LOGIN_URL env var if not set.")
    start_time: str
    duration_hours: float
    booker_first_name: str
    player_candidates: List[str]
    skip_weekends: bool = True
    skip_dates: List[str] = Field(default_factory=list)
    conditional_skip_rules: List[ConditionalSkipRule] = Field(default_factory=list)
