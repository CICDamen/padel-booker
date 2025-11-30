"""Pydantic models for the Padel Booker API."""

from pydantic import BaseModel, Field
from typing import List, Literal


class BookingRequest(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float
    booker_first_name: str
    player_candidates: List[str]
    device_mode: Literal["mobile", "desktop"] = Field(
        default="mobile",
        description="Device mode for booking: 'mobile' (29 days advance) or 'desktop' (28 days advance)"
    )


class ConfigModel(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float
