"""FastAPI service for Padel Booker."""

import os
import threading
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Security
from .models import BookingRequest
from .utils import run_booking_background, authenticate_user

app = FastAPI(title="Padel Booker API", version="1.0.0")

# Global variables for tracking booking status
booking_status = {"running": False, "result": None, "started_at": None}


@app.post("/api/book")
async def book_court(
    request: BookingRequest,
    authenticated: bool = Security(authenticate_user)
):
    """Start a booking process."""
    global booking_status

    if not authenticated:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if booking_status["running"]:
        raise HTTPException(status_code=400, detail="Booking already in progress")

    booker_username = os.getenv("BOOKER_USERNAME")
    booker_password = os.getenv("BOOKER_PASSWORD")

    if not booker_username or not booker_password:
        raise HTTPException(
            status_code=500,
            detail="BOOKER_USERNAME and BOOKER_PASSWORD environment variables must be set",
        )

    login_url = request.login_url or os.getenv("BOOKING_LOGIN_URL")
    if not login_url:
        raise HTTPException(
            status_code=400,
            detail="login_url required in request body or set BOOKING_LOGIN_URL env var",
        )

    booking_date = (datetime.now() + timedelta(days=request.days_offset)).strftime("%Y-%m-%d")

    thread = threading.Thread(
        target=run_booking_background,
        kwargs={
            "username": booker_username,
            "password": booker_password,
            "login_url": login_url,
            "booking_date": booking_date,
            "start_time": request.start_time,
            "duration_hours": request.duration_hours,
            "booker_first_name": request.booker_first_name,
            "player_candidates": request.player_candidates,
            "booking_status": booking_status,
            "skip_weekends": request.skip_weekends,
            "skip_dates": request.skip_dates or None,
            "conditional_skip_rules": request.conditional_skip_rules or None,
        },
    )
    thread.start()

    return {
        "status": "started",
        "message": "Booking process started",
        "booking_date": booking_date,
        "started_at": booking_status["started_at"],
    }


@app.get("/api/status")
async def get_status(authenticated: bool = Security(authenticate_user)):
    """Get current booking status."""
    if not authenticated:
        raise HTTPException(status_code=401, detail="Authentication failed")

    return {
        "running": booking_status["running"],
        "result": booking_status["result"],
        "started_at": booking_status["started_at"],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "padel-booker"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
