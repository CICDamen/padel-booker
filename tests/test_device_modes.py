"""Integration tests for mobile and desktop device modes."""

import pytest
from selenium.webdriver.common.by import By

from padel_booker.booker import PadelBooker


@pytest.mark.integration
class TestDeviceModes:
    """Test suite for verifying both mobile and desktop modes work correctly."""

    def test_booker_initialization(self, device_mode):
        """Test that PadelBooker initializes correctly for both modes."""
        booker = PadelBooker(device_mode=device_mode)
        assert booker.device_mode == device_mode
        assert booker.driver is not None
        assert booker.wait is not None
        assert booker.navigation_strategy is not None
        booker.driver.quit()

    def test_login(self, device_mode, booker_credentials):
        """Test login works in both mobile and desktop modes."""
        with PadelBooker(device_mode=device_mode) as booker:
            success = booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )
            assert success, f"Login should succeed in {device_mode} mode"

    def test_date_navigation(self, device_mode, booker_credentials, tomorrow_date):
        """Test date navigation works in both mobile and desktop modes."""
        with PadelBooker(device_mode=device_mode) as booker:
            # Login first
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )

            # Navigate to tomorrow
            booker.go_to_date(tomorrow_date)

            # Wait for matrix to load
            booker.wait_for_matrix_date(tomorrow_date)

            # Verify matrix container is present
            matrix = booker.driver.find_element(By.CLASS_NAME, "matrix-container")
            assert matrix is not None, f"Matrix should be present in {device_mode} mode"

    def test_slot_finding(self, device_mode, booker_credentials, tomorrow_date):
        """Test that slots can be found in both mobile and desktop modes."""
        with PadelBooker(device_mode=device_mode) as booker:
            # Login
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )

            # Navigate to date
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)

            # Find free slots
            free_slots = booker.driver.find_elements(By.CSS_SELECTOR, ".slot.normal.free")

            # Should have at least some free slots
            assert len(free_slots) > 0, f"Should find free slots in {device_mode} mode"

    def test_mobile_vs_desktop_slot_count(self, booker_credentials, tomorrow_date):
        """Test that both modes find the same slots on the same date."""
        mobile_count = 0
        desktop_count = 0

        # Get mobile slot count
        with PadelBooker(device_mode="mobile") as booker:
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)
            mobile_slots = booker.driver.find_elements(By.CSS_SELECTOR, ".slot.normal.free")
            mobile_count = len(mobile_slots)

        # Get desktop slot count
        with PadelBooker(device_mode="desktop") as booker:
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)
            desktop_slots = booker.driver.find_elements(By.CSS_SELECTOR, ".slot.normal.free")
            desktop_count = len(desktop_slots)

        # Both modes should find the same slots for the same date
        assert mobile_count == desktop_count, \
            f"Mobile ({mobile_count}) and desktop ({desktop_count}) should find same number of slots"


@pytest.mark.unit
class TestDeviceModeErrors:
    """Test error handling for device modes."""

    def test_invalid_device_mode(self):
        """Test that invalid device mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid device_mode"):
            PadelBooker(device_mode="invalid")

    def test_device_mode_validation_in_utils(self):
        """Test that setup_driver validates device mode."""
        from padel_booker.utils import setup_driver

        with pytest.raises(ValueError, match="Invalid device_mode"):
            setup_driver(device_mode="tablet")
