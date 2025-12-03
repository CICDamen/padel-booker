"""Integration tests for the complete booking flow (without final confirmation)."""

import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from padel_booker.booker import PadelBooker


@pytest.mark.integration
class TestBookingFlowIntegration:
    """Test the complete booking flow without making actual bookings."""

    def test_full_booking_flow_without_confirmation(
        self, booker_credentials, tomorrow_date
    ):
        """Test complete booking flow: login -> navigate -> find slot -> select players -> reach confirmation.

        This test verifies the entire flow works but does NOT click the final
        "Bevestigen" (Confirm) button, so no actual booking is made.

        Note: This test may skip if no slots are available, which is expected.
        """
        with PadelBooker() as booker:
            # Step 1: Login
            success = booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"],
            )
            assert success, "Login should succeed"

            # Step 2: Navigate to tomorrow's date
            booker.go_to_date(tomorrow_date)
            booker.wait_for_matrix_date(tomorrow_date)

            # Step 3: Try to find available consecutive slots using fallback
            # This searches backwards through workdays if tomorrow is fully booked
            slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
                tomorrow_date, "21:00", 1.5, max_days_back=7
            )

            # If still no slot found, try different times on tomorrow
            if not slot:
                for start_time in ["20:00", "19:00", "18:00", "17:00", "22:00"]:
                    slot, end_time = booker.find_consecutive_slots(start_time, 1.5)
                    if slot:
                        found_date = tomorrow_date
                        booker.logger.info(f"Found slot at {start_time} on {tomorrow_date}")
                        break

            # If no slots found at all, skip the test - this is expected in real scenarios
            if not slot:
                pytest.skip(
                    f"No available slots found on {tomorrow_date} or within 7 days before. "
                    "This is expected when the booking site is fully booked."
                )

            assert end_time is not None, "Should have an end time for the slot"
            booker.logger.info(f"Testing with slot on {found_date} from {slot} to {end_time}")

            # Step 4: Click on the slot to open booking form
            slot.click()

            # Wait for booking form to appear
            booker.wait.until(EC.presence_of_element_located((By.NAME, "players[2]")))

            # Select end time
            end_time_select = booker.driver.find_element(By.NAME, "end_time")
            for option in end_time_select.find_elements(By.TAG_NAME, "option"):
                if option.get_attribute("value") == end_time:
                    option.click()
                    break

            # Step 5: Select 3 players (speler 2, 3, 4)
            # We'll try to select any available players
            player_candidates = [
                "Test Player 1",
                "Test Player 2",
                "Test Player 3",
                "John Doe",
                "Jane Smith",
            ]

            selected_players = booker.select_players(player_candidates)
            assert len(selected_players) >= 3, "Should be able to select at least 3 players"

            # Step 6: Click "Verder" (Next/Continue) button
            verder_btn = booker.driver.find_element(
                By.CSS_SELECTOR, "input.button.submit[value='Verder']"
            )
            verder_btn.click()

            # Wait a moment for the page to process
            time.sleep(2)

            # Step 7: Verify we reached the confirmation page
            # Check for the "Bevestigen" (Confirm) button - but DON'T click it
            try:
                bevestigen_btn = booker.driver.find_element(
                    By.CSS_SELECTOR, "input.button.submit[value='Bevestigen']"
                )
                assert bevestigen_btn.is_displayed(), "Should see confirmation button"
                booker.logger.info("✅ Successfully reached confirmation page (did not confirm)")
            except TimeoutException:
                pytest.fail("Should have reached confirmation page with Bevestigen button")

            # We intentionally DO NOT click the Bevestigen button
            # This completes the test without making an actual booking

    def test_booking_flow_with_fallback_dates(
        self, booker_credentials, tomorrow_date
    ):
        """Test that backwards day search works in real integration scenario."""
        with PadelBooker() as booker:
            # Login
            success = booker.login(
                booker_credentials["username"],
                booker_credentials["password"],
                booker_credentials["login_url"],
            )
            assert success, "Login should succeed"

            # Use find_consecutive_slots_with_fallback to search backwards
            slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
                tomorrow_date, "21:00", 1.5, max_days_back=5
            )

            if slot and end_time and found_date:
                booker.logger.info(f"Found slot on {found_date} ending at {end_time}")
                # Verify the date is not in the future beyond tomorrow
                assert found_date <= tomorrow_date
            else:
                # It's okay if no slots found - we're just testing the mechanism works
                booker.logger.info("No slots found in the 5-day search window (this is okay)")
