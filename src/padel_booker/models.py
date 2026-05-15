"""Pydantic models for the Padel Booker API."""

from datetime import datetime, timedelta
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
