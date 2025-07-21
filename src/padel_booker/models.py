"""Pydantic models for the Padel Booker API."""

from pydantic import BaseModel
from typing import List


class BookingRequest(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float
    booker_first_name: str
    player_candidates: List[str]


class ConfigModel(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float
