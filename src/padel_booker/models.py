"""Pydantic models for the Padel Booker API."""

from pydantic import BaseModel


class BookingRequest(BaseModel):
    username: str
    password: str


class ConfigModel(BaseModel):
    login_url: str
    booking_date: str
    start_time: str
    duration_hours: float