"""Booking automation script."""
import os
import time
import re
from datetime import datetime
from typing import Optional, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    NoAlertPresentException,
)
from selenium.webdriver.support.ui import Select

from .utils import setup_driver, setup_logging, is_booking_enabled
from .exceptions import PlayerSelectionExhaustedError
from .navigation_strategy import get_navigation_strategy


class PadelBooker:
    """Automated padel court booking system."""

    def __init__(self, logger_name: str = "padel_booker", device_mode: str = "mobile"):
        """Initialize the PadelBooker with logger and driver setup.

        Args:
            logger_name: Name for the logger
            device_mode: Either 'mobile' or 'desktop' (default: 'mobile')
        """
        self.logger = setup_logging(logger_name)
        self.device_mode = device_mode
        self.driver, self.wait = setup_driver(device_mode)
        self.navigation_strategy = get_navigation_strategy(device_mode)
        self.logger.info("Initialized PadelBooker in %s mode", device_mode)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup driver."""
        _ = exc_type, exc_val, exc_tb  # Unused but required for context manager protocol
        if self.driver:
            self.driver.quit()

    def login(self, username: str, password: str, url: str) -> bool:
        """Logs in to the booking system."""
        try:
            self.logger.info("Logging in to %s...", url)
            self.driver.get(url)

            # Use name attributes for input fields
            self.driver.find_element(By.NAME, "username").send_keys(username)
            self.driver.find_element(By.NAME, "password").send_keys(password)
            # Find the login button within the form
            login_button = self.driver.find_element(
                By.CSS_SELECTOR, "#login-form button"
            )
            login_button.click()

            # Wait for the login form to disappear (or for a post-login element to appear)
            self.wait.until(EC.invisibility_of_element_located((By.ID, "login-form")))
            self.logger.info("Login successful")
            return True

        except (NoSuchElementException, TimeoutException) as e:
            self.logger.error("Login failed: %s", e)
            return False

    def check_availability(
        self, date: str, start_time: str, duration_hours: float
    ) -> Optional[Any]:
        """Checks the availability of a time slot with a specific start time and duration (in hours)."""
        try:
            self.logger.info(
                "Checking availability for %s at %s for %s hours",
                date,
                start_time,
                duration_hours,
            )
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "matrix-container"))
            )
            available_slots = self.driver.find_elements(
                By.CSS_SELECTOR, ".slot.normal.free"
            )
            self.logger.info("Found %d free slots on the page.", len(available_slots))

            for slot in available_slots:
                try:
                    period_div = slot.find_element(By.CLASS_NAME, "slot-period")
                    period_text = period_div.text.strip()
                    self.logger.info("Free slot: %s", period_text)
                    start, end = [t.strip() for t in period_text.split("-")]
                    if start == start_time:
                        fmt = "%H:%M"
                        start_dt = datetime.strptime(start, fmt)
                        end_dt = datetime.strptime(end, fmt)
                        duration = (end_dt - start_dt).total_seconds() / 3600
                        if abs(duration - duration_hours) < 0.01:
                            self.logger.info("Found available slot: %s", period_text)
                            return slot
                except (NoSuchElementException, TimeoutException) as e:
                    self.logger.warning("Error parsing slot: %s", e)

            self.logger.info("Desired time slot not available")
            return None
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.error("Error checking availability: %s", str(e))
            return None

    def select_players(self, player_candidates: list[str]) -> list[str]:
        """Selects 3 available players from the provided list and adds them as speler 2/3/4."""
        selected = []
        used_candidates = set()

        for idx in range(2, 5):  # speler 2, 3, 4
            select_elem = self.driver.find_element(By.NAME, f"players[{idx}]")
            select = Select(select_elem)
            found = False

            for candidate in player_candidates:
                if candidate in used_candidates:
                    continue
                # Try to find an option with the candidate's name
                for option in select.options:
                    if option.text.strip() == candidate:
                        select.select_by_visible_text(candidate)
                        self.logger.info("Selected %s as speler %d", candidate, idx)
                        selected.append(candidate)
                        used_candidates.add(candidate)
                        found = True
                        break
                if found:
                    break

            if not found:
                self.logger.error(
                    "Could not find an available player for speler %d", idx
                )
                return selected

        return selected

    def make_booking(
        self, slot_element: Any, guest_details: dict[str, str]
    ) -> dict[str, Any]:
        """Makes a booking for the selected time slot."""
        try:
            self.logger.info("Making booking...")
            slot_element.click()
            self.wait.until(EC.presence_of_element_located((By.ID, "booking-form")))

            self.driver.find_element(By.ID, "guest-name").send_keys(
                guest_details["name"]
            )
            self.driver.find_element(By.ID, "email").send_keys(guest_details["email"])
            self.driver.find_element(By.ID, "phone").send_keys(guest_details["phone"])
            self.driver.find_element(By.ID, "confirm-booking").click()

            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "booking-confirmed"))
            )
            confirmation_number = self.driver.find_element(
                By.CLASS_NAME, "confirmation-number"
            ).text
            self.logger.info("Booking confirmed: %s", confirmation_number)

            return {
                "status": "success",
                "confirmation_number": confirmation_number,
                "timestamp": datetime.now().isoformat(),
            }
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.error("Booking failed: %s", str(e))
            return {"status": "error", "message": str(e)}

    def go_to_date(self, target_date: str):
        """Navigates to the target date (format: YYYY-MM-DD).

        Uses the appropriate navigation strategy based on device mode.
        """
        self.navigation_strategy.navigate_to_date(
            self.driver, self.wait, self.logger, target_date
        )

    def wait_for_matrix_date(self, target_date: str):
        """Waits until the matrix table is showing the correct date.

        Uses the appropriate navigation strategy based on device mode.
        """
        self.navigation_strategy.wait_for_matrix_date(
            self.driver, self.wait, self.logger, target_date
        )

    def find_consecutive_slots(self, start_time: str, duration_hours: float):
        """Finds a court with enough consecutive free slots starting at start_time to cover duration_hours."""
        available_slots = self.driver.find_elements(
            By.CSS_SELECTOR, ".slot.normal.free"
        )
        slots_by_court = {}

        # Group slots by court (using the slot's 'title' attribute)
        for slot in available_slots:
            try:
                period_div = slot.find_element(By.CLASS_NAME, "slot-period")
                period_text = period_div.text.strip()
                start, end = [t.strip() for t in period_text.split("-")]
                court = slot.get_attribute("title")  # e.g., "Padel indoor 2"
                if court not in slots_by_court:
                    slots_by_court[court] = []
                slots_by_court[court].append((start, end, slot))
            except (NoSuchElementException, ValueError, IndexError):
                continue

        fmt = "%H:%M"
        needed_minutes = int(duration_hours * 60)

        for court, slots in slots_by_court.items():
            # Sort slots by start time
            slots.sort(key=lambda x: datetime.strptime(x[0], fmt))

            for i, (start, end, slot_elem) in enumerate(slots):
                if start != start_time:
                    continue

                # Try to chain slots
                total_minutes = (
                    datetime.strptime(end, fmt) - datetime.strptime(start, fmt)
                ).seconds // 60
                j = i
                last_end = end

                while total_minutes < needed_minutes and j + 1 < len(slots):
                    next_start, next_end, _ = slots[j + 1]
                    if next_start == last_end:
                        total_minutes += (
                            datetime.strptime(next_end, fmt)
                            - datetime.strptime(next_start, fmt)
                        ).seconds // 60
                        last_end = next_end
                        j += 1
                    else:
                        break

                if total_minutes >= needed_minutes:
                    self.logger.info(
                        "Found consecutive slots on %s from %s to %s",
                        court,
                        start_time,
                        last_end,
                    )
                    return slot_elem, last_end

        self.logger.info("No consecutive slots found for the requested duration")
        return None, None

    def try_booking_with_player_rotation(
        self, player_candidates: list[str], booker_first_name: str
    ):
        """Tries to make a booking by selecting players and handling blocked player errors."""
        candidates = player_candidates[:]
        blocked_players = set()
        max_attempts = int(os.getenv("MAX_BOOKING_ATTEMPTS", "2"))
        attempt_count = 0

        while len(candidates) >= 3 and attempt_count < max_attempts:
            attempt_count += 1

            # Keep track of already tried players to avoid loops
            for blocked in blocked_players:
                if blocked in candidates:
                    # Remove any players we've already identified as blocked
                    candidates = [p for p in candidates if p != blocked]

            if len(candidates) < 3:
                self.logger.error("Not enough non-blocked players available after removing: %s",
                                  ", ".join(blocked_players))
                raise PlayerSelectionExhaustedError(
                    f"Not enough players available after removing blocked players: {blocked_players}"
                )

            # Deselect and reselect players each time
            selected = self.select_players(candidates)
            if len(selected) < 3:
                self.logger.error("Not enough available players to proceed.")
                raise PlayerSelectionExhaustedError("Could not select enough players")

            # Click the 'Verder' button
            verder_btn = self.driver.find_element(By.ID, "__make_submit")
            verder_btn.click()
            time.sleep(1)  # Wait for possible popup or page update

            # Try to detect alert (JS alert)
            error_text = None
            try:
                alert = self.driver.switch_to.alert
                error_text = alert.text
                alert.accept()
            except NoAlertPresentException:
                # Check for custom modal/pop-up
                try:
                    popup = self.driver.find_element(By.CLASS_NAME, "swal2-popup")
                    if popup.is_displayed():
                        error_text = popup.text
                        close_btns = popup.find_elements(By.TAG_NAME, "button")
                        for btn in close_btns:
                            if btn.is_displayed():
                                btn.click()
                                break
                except (NoSuchElementException, TimeoutException):
                    pass

            if error_text:
                self.logger.warning("Booking error popup: %s", error_text)
                m = re.search(r"\[\d+] ([^ ]+) [^ ]+ mag niet meer spelen", error_text)
                if m:
                    blocked = m.group(1)
                    self.logger.info("Blocked player detected: %s", blocked)
                    if blocked == booker_first_name:
                        self.logger.error(
                            "Booker %s is blocked. Cancelling booking attempt.",
                            booker_first_name,
                        )
                        return None

                    # Add the blocked player to the blocked set
                    blocked_players.add(blocked)

                    # Create a new candidates list without the blocked players
                    candidates = [p for p in player_candidates if p not in blocked_players]

                    # Check if we have enough players left
                    if len(candidates) < 3:
                        self.logger.error(
                            "Not enough players left after removing blocked players: %s",
                            ", ".join(blocked_players)
                        )
                        raise PlayerSelectionExhaustedError(
                            f"Not enough players available after removing blocked players: {blocked_players}"
                        )
                    continue
                else:
                    self.logger.error("Unknown booking error, aborting.")
                    return None
            else:
                # No error popup detected, proceed with final booking confirmation
                try:
                    if is_booking_enabled():
                        self.logger.info("BOOKING ENABLED: Confirming actual booking")
                        confirm_btn = self.driver.find_element(By.ID, "__make_submit2")
                        confirm_btn.click()
                        time.sleep(2)  # Wait for booking confirmation
                    else:
                        self.logger.info("BOOKING DISABLED: Skipping final confirmation (dry-run mode)")

                    self.logger.info("Players selected for booking: %s", selected)
                    # self.logger.info(f"Booking confirmed with players: {selected}")
                    return selected
                except (NoSuchElementException, TimeoutException) as e:
                    self.logger.error(
                        "Failed to find or click confirmation button: %s", e
                    )
                    return None

        # If we've exhausted our attempts or don't have enough candidates
        if attempt_count >= max_attempts:
            self.logger.error("Maximum booking attempts reached (%d)", max_attempts)
            raise PlayerSelectionExhaustedError(f"Maximum booking attempts reached ({max_attempts})")
        else:
            self.logger.error("Ran out of player candidates for booking.")
            raise PlayerSelectionExhaustedError("Not enough players available for booking")

    def book_slot(
        self, slot, end_time: str, player_candidates: list[str], booker_first_name: str
    ):
        """Books a slot by clicking it, selecting end time, and attempting booking with player rotation."""
        try:
            slot.click()
            self.wait.until(EC.presence_of_element_located((By.NAME, "players[2]")))

            # Select the end time
            end_time_select = self.driver.find_element(By.NAME, "end_time")
            for option in end_time_select.find_elements(By.TAG_NAME, "option"):
                if option.get_attribute("value") == end_time:
                    option.click()
                    break

            # Try booking with player rotation
            try:
                selected = self.try_booking_with_player_rotation(
                    player_candidates, booker_first_name
                )
                return selected
            except PlayerSelectionExhaustedError as e:
                self.logger.error("Player selection exhausted: %s", str(e))
                return None

        except (NoSuchElementException, TimeoutException) as e:
            self.logger.error("Error during slot booking: %s", e)
            return None
