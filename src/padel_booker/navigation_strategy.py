"""Navigation strategies for different device modes (mobile vs desktop)."""

import time
import datetime as dt
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.ui import WebDriverWait
    import logging


class NavigationStrategy(ABC):
    """Base class for navigation strategies."""

    @abstractmethod
    def navigate_to_date(
        self, driver: "WebDriver", wait: "WebDriverWait", logger: "logging.Logger", target_date: str
    ) -> None:
        """Navigate to the target date (format: YYYY-MM-DD).

        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
            logger: Logger for output
            target_date: Target date in YYYY-MM-DD format
        """
        pass

    @abstractmethod
    def wait_for_matrix_date(
        self, driver: "WebDriver", wait: "WebDriverWait", logger: "logging.Logger", target_date: str
    ) -> None:
        """Wait until the matrix is showing the correct date.

        Args:
            driver: Selenium WebDriver instance
            wait: WebDriverWait instance
            logger: Logger for output
            target_date: Target date in YYYY-MM-DD format
        """
        pass


class DesktopNavigationStrategy(NavigationStrategy):
    """Navigation strategy for desktop mode using calendar clicks."""

    def navigate_to_date(
        self, driver: "WebDriver", wait: "WebDriverWait", logger: "logging.Logger", target_date: str
    ) -> None:
        """Navigate to target date using desktop calendar navigation."""
        try:
            # Parse target date
            target_dt = dt.datetime.strptime(target_date, "%Y-%m-%d").date()
            year = target_dt.year
            month = target_dt.month
            day = target_dt.day

            logger.info("Navigating to date: %s (desktop mode)", target_date)

            # First, navigate to the correct month/year if needed
            wait.until(EC.presence_of_element_located((By.ID, "calendar_date_title")))

            max_month_navigation = 24  # Prevent infinite loops
            navigation_count = 0

            while navigation_count < max_month_navigation:
                # Get current month/year from calendar title
                calendar_title = driver.find_element(By.ID, "calendar_date_title").text.strip()
                try:
                    # Parse "Nov 2025" format
                    month_names = [
                        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
                    ]
                    parts = calendar_title.split()
                    current_month_str = parts[0]
                    current_year = int(parts[1])
                    current_month = month_names.index(current_month_str.title()) + 1
                except (ValueError, IndexError) as e:
                    logger.error("Failed to parse calendar title '%s': %s", calendar_title, e)
                    break

                if current_year == year and current_month == month:
                    # We're in the right month, now click the specific date
                    break
                elif (current_year < year) or (current_year == year and current_month < month):
                    # Need to go forward
                    next_btn = driver.find_element(By.CSS_SELECTOR, ".month.next a")
                    next_btn.click()
                else:
                    # Need to go backward
                    prev_btn = driver.find_element(By.CSS_SELECTOR, ".month.prev a")
                    prev_btn.click()

                navigation_count += 1
                time.sleep(0.5)  # Brief pause between navigation clicks
                wait.until(EC.presence_of_element_located((By.ID, "calendar_date_title")))

            if navigation_count >= max_month_navigation:
                logger.error("Exceeded maximum month navigation attempts")
                return

            # Now click on the specific date
            date_id = f"cal_{year}_{month}_{day}"
            try:
                date_cell = driver.find_element(By.ID, date_id)
                date_link = date_cell.find_element(By.CLASS_NAME, "cal-link")
                date_link.click()
                logger.info("Successfully navigated to %s", target_date)

                # Wait for the matrix to load for the new date
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "matrix-container")))

            except (NoSuchElementException, TimeoutException) as e:
                logger.error("Failed to click on date %s: %s", target_date, e)

        except ValueError as e:
            logger.error("Invalid date format '%s': %s", target_date, e)
        except (NoSuchElementException, TimeoutException) as e:
            logger.error("Error navigating to date: %s", e)

    def wait_for_matrix_date(
        self, driver: "WebDriver", wait: "WebDriverWait", logger: "logging.Logger", target_date: str
    ) -> None:
        """Wait until the matrix table is showing the correct date (desktop mode)."""

        def date_matches(driver):
            try:
                date_title = driver.find_element(By.ID, "matrix_date_title").text.strip()
                # Parse "Zo 30-11-2025" format
                date_str = date_title.split()[-1]
                current_date = dt.datetime.strptime(date_str, "%d-%m-%Y").date()
                target_dt = dt.datetime.strptime(target_date, "%Y-%m-%d").date()
                return current_date == target_dt
            except (ValueError, IndexError, NoSuchElementException) as e:
                logger.warning("Error parsing date in wait_for_matrix_date: %s", e)
                return False

        wait.until(date_matches)


class MobileNavigationStrategy(NavigationStrategy):
    """Navigation strategy for mobile mode using form dropdowns."""

    def navigate_to_date(
        self, driver: "WebDriver", wait: "WebDriverWait", logger: "logging.Logger", target_date: str
    ) -> None:
        """Navigate to target date using mobile form dropdown."""
        try:
            logger.info("Navigating to date: %s (mobile mode)", target_date)

            # Wait for the schedule form to be present
            wait.until(EC.presence_of_element_located((By.ID, "schedule-index")))

            # Find the date dropdown
            date_select_element = driver.find_element(By.CSS_SELECTOR, "select[name='date']")
            date_select = Select(date_select_element)

            # Select the target date
            try:
                date_select.select_by_value(target_date)
                logger.info("Successfully selected date %s in dropdown", target_date)

                # Wait for the matrix to reload
                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "matrix-container")))

            except NoSuchElementException as e:
                logger.error("Date %s not available in dropdown: %s", target_date, e)
                # Log available dates for debugging
                available_dates = [opt.get_attribute("value") for opt in date_select.options if opt.get_attribute("value")]
                logger.info("Available dates: %s", available_dates)
                raise

        except (NoSuchElementException, TimeoutException) as e:
            logger.error("Error navigating to date in mobile mode: %s", e)
            raise

    def wait_for_matrix_date(
        self, driver: "WebDriver", wait: "WebDriverWait", logger: "logging.Logger", target_date: str
    ) -> None:
        """Wait until the matrix is showing the correct date (mobile mode).

        In mobile mode, we check the selected value in the date dropdown.
        """

        def date_matches(driver):
            try:
                date_select_element = driver.find_element(By.CSS_SELECTOR, "select[name='date']")
                date_select = Select(date_select_element)
                selected_value = date_select.first_selected_option.get_attribute("value")
                return selected_value == target_date
            except (NoSuchElementException, ValueError) as e:
                logger.warning("Error checking selected date in wait_for_matrix_date: %s", e)
                return False

        wait.until(date_matches)


def get_navigation_strategy(device_mode: str) -> NavigationStrategy:
    """Factory function to get the appropriate navigation strategy.

    Args:
        device_mode: Either 'mobile' or 'desktop'

    Returns:
        NavigationStrategy instance

    Raises:
        ValueError: If device_mode is not 'mobile' or 'desktop'
    """
    if device_mode == "mobile":
        return MobileNavigationStrategy()
    elif device_mode == "desktop":
        return DesktopNavigationStrategy()
    else:
        raise ValueError(f"Invalid device_mode: {device_mode}. Must be 'mobile' or 'desktop'")
