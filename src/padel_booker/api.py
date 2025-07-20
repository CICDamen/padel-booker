"""FastAPI service for Padel Booker."""

import json
import os
import threading
from typing import Dict
from fastapi import FastAPI, HTTPException, Depends
from .models import BookingRequest, ConfigModel
from .utils import run_booking_background, authenticate_user

app = FastAPI(title="Padel Booker API", version="1.0.0")

# Global variables for tracking booking status
booking_status = {"running": False, "result": None, "started_at": None}



def load_config() -> Dict:
    """Load configuration from config.json."""
    config_path = os.path.join('data', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as f:
            return json.load(f)
    return {}



@app.post("/api/book")
async def book_court(request: BookingRequest, username: str = Depends(authenticate_user)):
    """Start a booking process."""
    global booking_status
    
    if booking_status["running"]:
        raise HTTPException(status_code=400, detail="Booking already in progress")
    
    config = load_config()
    if not config:
        raise HTTPException(status_code=400, detail="No configuration found")
    
    # Get booker credentials from environment variables
    booker_username = os.getenv('BOOKER_USERNAME')
    booker_password = os.getenv('BOOKER_PASSWORD')
    
    if not booker_username or not booker_password:
        raise HTTPException(status_code=500, detail="BOOKER_USERNAME and BOOKER_PASSWORD environment variables must be set")
    
    # Start booking in background thread
    thread = threading.Thread(
        target=run_booking_background, 
        args=(config, booker_username, booker_password, request.booker_first_name, request.player_candidates, booking_status)
    )
    thread.start()
    
    return {
        "status": "started", 
        "message": "Booking process started",
        "started_at": booking_status["started_at"]
    }


@app.get("/api/status")
async def get_status(username: str = Depends(authenticate_user)):
    """Get current booking status."""
    return {
        "running": booking_status["running"],
        "result": booking_status["result"],
        "started_at": booking_status["started_at"]
    }


@app.get("/api/config")
async def get_config(username: str = Depends(authenticate_user)):
    """Get current configuration."""
    return load_config()


@app.post("/api/config")
async def update_config(config: ConfigModel, username: str = Depends(authenticate_user)):
    """Update configuration."""
    config_path = os.path.join('data', 'config.json')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config.dict(), f, indent=2)
    
    return {"status": "success", "message": "Configuration updated"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "padel-booker"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8080)