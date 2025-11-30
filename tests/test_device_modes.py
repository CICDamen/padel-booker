"""Integration tests for mobile and desktop device modes."""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

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

    def test_booking_form_buttons(self, device_mode, booker_credentials, tomorrow_date):
        """Test that booking form buttons (Verder/Bevestigen) can be found in both modes."""
        with PadelBooker(device_mode=device_mode) as booker:
            # Login and navigate
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)

            # Find and click a free slot
            free_slots = booker.driver.find_elements(By.CSS_SELECTOR, ".slot.normal.free")
            assert len(free_slots) > 0, "Should have free slots available"
            free_slots[0].click()
            time.sleep(2)

            # Verify 'Verder' button is found with the correct selector
            verder_btn = booker.driver.find_element(
                By.CSS_SELECTOR, "input.button.submit[value='Verder']"
            )
            assert verder_btn is not None, f"Verder button should be found in {device_mode} mode"
            assert verder_btn.get_attribute("value") == "Verder"

            # Select players to enable form submission
            for idx in range(2, 5):
                select_elem = booker.driver.find_element(By.NAME, f"players[{idx}]")
                select = Select(select_elem)
                # Select first non-empty option
                for option in select.options:
                    if option.text.strip() and option.get_attribute("value"):
                        select.select_by_visible_text(option.text)
                        break

            # Click Verder to go to confirmation page
            verder_btn.click()
            time.sleep(2)

            # Verify 'Bevestigen' button is found with the correct selector
            bevestigen_btn = booker.driver.find_element(
                By.CSS_SELECTOR, "input.button.submit[value='Bevestigen']"
            )
            assert bevestigen_btn is not None, f"Bevestigen button should be found in {device_mode} mode"
            assert bevestigen_btn.get_attribute("value") == "Bevestigen"

    def test_player_selection_dropdowns(self, device_mode, booker_credentials, tomorrow_date):
        """Test that player selection dropdowns work correctly in both modes."""
        with PadelBooker(device_mode=device_mode) as booker:
            # Login and navigate
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)

            # Find and click a free slot
            free_slots = booker.driver.find_elements(By.CSS_SELECTOR, ".slot.normal.free")
            assert len(free_slots) > 0, "Should have free slots available"
            free_slots[0].click()
            time.sleep(2)

            # Verify all player dropdowns (2, 3, 4) exist and have options
            for idx in range(2, 5):
                select_elem = booker.driver.find_element(By.NAME, f"players[{idx}]")
                assert select_elem is not None, f"Player {idx} dropdown should exist"

                select = Select(select_elem)
                assert len(select.options) > 0, f"Player {idx} dropdown should have options"

    def test_find_consecutive_slots(self, device_mode, booker_credentials, tomorrow_date):
        """Test that find_consecutive_slots works on the real website."""
        with PadelBooker(device_mode=device_mode) as booker:
            # Login and navigate
            booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"]
            )
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)

            # Try to find consecutive slots for 1 hour (should be easy to find)
            slot, end_time = booker.find_consecutive_slots("09:00", 1.0)

            # We may or may not find slots depending on availability,
            # but the method should not crash
            if slot is not None:
                assert end_time is not None, "If slot found, end_time should be set"


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
