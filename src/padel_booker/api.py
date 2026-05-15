"""FastAPI service for Padel Booker."""

import os
import threading
from fastapi import FastAPI, HTTPException, Security
from pydantic import ValidationError
from .models import BookingRequest
from .utils import run_booking_background, authenticate_user, load_booking_config

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

    try:
        config = load_booking_config()
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=f"Booking config incomplete: {e}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    thread = threading.Thread(
        target=run_booking_background,
        kwargs={
            "username": booker_username,
            "password": booker_password,
            "login_url": config.login_url,
            "booking_date": request.booking_date,
            "start_time": config.start_time,
            "duration_hours": config.duration_hours,
            "booker_first_name": request.booker_first_name,
            "player_candidates": request.player_candidates,
            "booking_status": booking_status,
            "skip_weekends": config.skip_weekends,
            "skip_dates": config.skip_dates or None,
            "conditional_skip_rules": config.conditional_skip_rules or None,
        },
    )
    thread.start()

    return {
        "status": "started",
        "message": "Booking process started",
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
