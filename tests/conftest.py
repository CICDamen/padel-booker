"""Pytest configuration and fixtures for padel-booker tests."""

import os
import pytest
from datetime import datetime, timedelta


@pytest.fixture
def booker_credentials():
    """Fixture providing booker credentials from environment."""
    username = os.getenv("BOOKER_USERNAME")
    password = os.getenv("BOOKER_PASSWORD")

    if not username or not password:
        pytest.skip("BOOKER_USERNAME and BOOKER_PASSWORD environment variables must be set")

    return {
        "username": username,
        "password": password,
        "login_url": "https://houten.baanreserveren.nl/"
    }


@pytest.fixture
def tomorrow_date():
    """Fixture providing tomorrow's date in YYYY-MM-DD format."""
    return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")


@pytest.fixture
def chromedriver_path():
    """Fixture providing chromedriver path."""
    path = os.getenv("CHROMEDRIVER_PATH")
    if not path:
        pytest.skip("CHROMEDRIVER_PATH environment variable must be set")
    return path
