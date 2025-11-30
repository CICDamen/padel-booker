"""FastAPI service for Padel Booker."""

import os
import threading
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

    # Verify authentication was successful
    if not authenticated:
        raise HTTPException(status_code=401, detail="Authentication failed")

    if booking_status["running"]:
        raise HTTPException(status_code=400, detail="Booking already in progress")

    # Get booker credentials from environment variables
    booker_username = os.getenv("BOOKER_USERNAME")
    booker_password = os.getenv("BOOKER_PASSWORD")

    if not booker_username or not booker_password:
        raise HTTPException(
            status_code=500,
            detail="BOOKER_USERNAME and BOOKER_PASSWORD environment variables must be set",
        )

    # Start booking in background thread with all parameters from the request
    thread = threading.Thread(
        target=run_booking_background,
        args=(
            booker_username,
            booker_password,
            request.login_url,
            request.booking_date,
            request.start_time,
            request.duration_hours,
            request.booker_first_name,
            request.player_candidates,
            booking_status,
            request.device_mode,
        ),
    )
    thread.start()

    return {
        "status": "started",
        "message": "Booking process started",
        "started_at": booking_status["started_at"],
        "device_mode": request.device_mode,
    }


@app.get("/api/status")
async def get_status(authenticated: bool = Security(authenticate_user)):
    """Get current booking status."""
    # Verify authentication was successful
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
