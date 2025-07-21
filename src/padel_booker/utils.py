"""Utility functions for the booking automation."""

import logging
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

security = HTTPBasic()


def is_booking_enabled() -> bool:
    """
    Check if actual booking confirmation is enabled based on environment variable.

    Returns:
        bool: True if ENABLE_BOOKING environment variable is set to 'true', False otherwise
    """
    return os.environ.get("ENABLE_BOOKING", "false").lower() == "true"


def setup_driver() -> tuple[webdriver.Chrome, WebDriverWait]:
    """Sets up the Selenium driver and wait."""
    chrome_options = Options()

    # Use Chrome options from environment variable if available
    chrome_opts_env = os.getenv("CHROME_OPTIONS")
    if chrome_opts_env:
        for option in chrome_opts_env.split():
            chrome_options.add_argument(option)
    else:
        # Fallback to hardcoded options
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

    # Set path to ChromeDriver from environment variable
    chrome_driver_path = os.getenv("CHROMEDRIVER_PATH")
    if not chrome_driver_path:
        raise RuntimeError("CHROMEDRIVER_PATH environment variable is not set")
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements
    return driver, wait


def setup_logging(name=None) -> logging.Logger:
    """Sets up logging and returns a logger

    Args:
        name: Optional name for the logger. If None, uses the module name.
    """
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(name or __name__)


def load_config(config_path: str | None = None) -> dict:
    """Loads the configuration from a file

    Args:
        config_path: Path to the configuration file.
        Defaults to 'data/config.json' relative to project root.
    """
    try:
        if config_path is None:
            # Find project root (the directory containing this file, then go up one level)
            project_root = Path(__file__).parent.parent.resolve()
            config_path = project_root / "data" / "config.json"
        else:
            config_path = Path(config_path)
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
        return config
    except Exception as e:
        raise RuntimeError(f"Failed to load config from {config_path}: {e}") from e


def run_booking_background(
    config: Dict,
    username: str,
    password: str,
    booker_first_name: str,
    player_candidates: list[str],
    booking_status: Dict,
):
    """Run booking in background thread."""
    from .booker import PadelBooker

    try:
        booking_status["running"] = True
        booking_status["result"] = None
        booking_status["started_at"] = datetime.now().isoformat()

        if not booker_first_name or not player_candidates:
            booking_status["result"] = {
                "status": "error",
                "message": "booker_first_name and player_candidates must be provided",
            }
            return

        with PadelBooker() as booker:
            # Login
            if not booker.login(username, password, config["login_url"]):
                booking_status["result"] = {
                    "status": "error",
                    "message": "Login failed",
                }
                return

            # Navigate to booking date
            booker.go_to_date(config["booking_date"])
            booker.wait_for_matrix_date(config["booking_date"])

            # Find consecutive slots
            slot, end_time = booker.find_consecutive_slots(
                config["start_time"], config["duration_hours"]
            )

            if not slot:
                booking_status["result"] = {
                    "status": "error",
                    "message": f"No available slots found for {config['start_time']} on {config['booking_date']}",
                }
                return

            # Try booking
            selected_players = booker.book_slot(
                slot, end_time, player_candidates, booker_first_name
            )

            if selected_players:
                booking_status["result"] = {
                    "status": "success",
                    "message": f"Booking successful with players: {selected_players}",
                    "players": selected_players,
                }
            else:
                booking_status["result"] = {
                    "status": "error",
                    "message": "Booking failed",
                }

    except Exception as e:
        booking_status["result"] = {"status": "error", "message": f"Error: {str(e)}"}
    finally:
        booking_status["running"] = False


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate user with basic auth using environment variables."""
    correct_username = os.getenv("API_USERNAME")
    correct_password = os.getenv("API_PASSWORD")

    if not correct_username or not correct_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication not configured - API_USERNAME and API_PASSWORD environment variables must be set",
        )

    is_correct_username = secrets.compare_digest(credentials.username, correct_username)
    is_correct_password = secrets.compare_digest(credentials.password, correct_password)

    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
