"""Pydantic models for the Padel Booker API."""

from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import List


class BookingRequest(BaseModel):
    login_url: str
    booking_date: str = Field(
        default_factory=lambda: (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    )
    start_time: str
    duration_hours: float
    booker_first_name: str
    player_candidates: List[str]


class ConfigModel(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float
