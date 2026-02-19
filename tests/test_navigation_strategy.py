"""Unit tests for navigation strategies."""

import pytest
from unittest.mock import Mock, patch

from padel_booker.navigation_strategy import (
    NavigationStrategy,
    DesktopNavigationStrategy,
    MobileNavigationStrategy,
    get_navigation_strategy,
    parse_month_abbreviation,
)


@pytest.mark.unit
class TestNavigationStrategyFactory:
    """Test the navigation strategy factory function."""

    def test_get_mobile_strategy(self):
        """Test factory returns MobileNavigationStrategy for 'mobile'."""
        strategy = get_navigation_strategy("mobile")
        assert isinstance(strategy, MobileNavigationStrategy)

    def test_get_desktop_strategy(self):
        """Test factory returns DesktopNavigationStrategy for 'desktop'."""
        strategy = get_navigation_strategy("desktop")
        assert isinstance(strategy, DesktopNavigationStrategy)

    def test_invalid_mode_raises_error(self):
        """Test factory raises ValueError for invalid mode."""
        with pytest.raises(ValueError, match="Invalid device_mode"):
            get_navigation_strategy("invalid")


@pytest.mark.unit
class TestMobileNavigationStrategy:
    """Test MobileNavigationStrategy."""

    def test_navigate_to_date_success(self):
        """Test successful date navigation in mobile mode."""
        strategy = MobileNavigationStrategy()

        # Mock driver and wait
        mock_driver = Mock()
        mock_wait = Mock()
        mock_logger = Mock()

        # Mock form and select element
        mock_select_element = Mock()
        mock_select = Mock()

        with patch("padel_booker.navigation_strategy.Select", return_value=mock_select):
            mock_driver.find_element.return_value = mock_select_element

            # Call navigate_to_date
            strategy.navigate_to_date(mock_driver, mock_wait, mock_logger, "2025-12-01")

            # Verify select was called with correct date
            mock_select.select_by_value.assert_called_once_with("2025-12-01")

    def test_wait_for_matrix_date(self):
        """Test waiting for matrix date in mobile mode."""
        strategy = MobileNavigationStrategy()

        mock_driver = Mock()
        mock_wait = Mock()
        mock_logger = Mock()

        # Mock the select element
        mock_select_element = Mock()
        mock_select = Mock()
        mock_option = Mock()
        mock_option.get_attribute.return_value = "2025-12-01"
        mock_select.first_selected_option = mock_option

        with patch("padel_booker.navigation_strategy.Select", return_value=mock_select):
            mock_driver.find_element.return_value = mock_select_element

            # Mock wait.until to call the condition immediately
            def call_condition(condition):
                return condition(mock_driver)

            mock_wait.until.side_effect = call_condition

            # Should not raise
            strategy.wait_for_matrix_date(mock_driver, mock_wait, mock_logger, "2025-12-01")


@pytest.mark.unit
class TestDesktopNavigationStrategy:
    """Test DesktopNavigationStrategy."""

    def test_navigate_to_date_same_month(self):
        """Test date navigation when target is in current month."""
        strategy = DesktopNavigationStrategy()

        mock_driver = Mock()
        mock_wait = Mock()
        mock_logger = Mock()

        # Mock calendar title showing Nov 2025
        mock_calendar_title = Mock()
        mock_calendar_title.text = "Nov 2025"

        # Mock date link that will be returned by wait.until
        mock_date_link = Mock()

        def mock_find_element(by, value):
            if value == "calendar_date_title":
                return mock_calendar_title
            return Mock()

        mock_driver.find_element.side_effect = mock_find_element

        # Track how many times wait.until is called to return different things
        wait_call_count = [0]

        def mock_until(condition):
            wait_call_count[0] += 1
            # First call: wait for calendar_date_title presence (line 68)
            # Second call: wait for date cell presence (line 114)
            # Third call: wait for date link to be clickable (line 116-118) - return mock_date_link
            if wait_call_count[0] == 3:
                return mock_date_link
            # Fourth call: wait for matrix-container (line 124)
            return Mock()

        mock_wait.until.side_effect = mock_until

        # Call navigate_to_date for a date in Nov 2025
        strategy.navigate_to_date(mock_driver, mock_wait, mock_logger, "2025-11-15")

        # Verify date link was clicked
        mock_date_link.click.assert_called_once()

    def test_wait_for_matrix_date(self):
        """Test waiting for matrix date in desktop mode."""
        strategy = DesktopNavigationStrategy()

        mock_driver = Mock()
        mock_wait = Mock()
        mock_logger = Mock()

        # Mock matrix_date_title element
        mock_matrix_title = Mock()
        mock_matrix_title.text = "Zo 01-12-2025"

        mock_driver.find_element.return_value = mock_matrix_title

        # Mock wait.until to call the condition immediately
        def call_condition(condition):
            return condition(mock_driver)

        mock_wait.until.side_effect = call_condition

        # Should not raise
        strategy.wait_for_matrix_date(mock_driver, mock_wait, mock_logger, "2025-12-01")


@pytest.mark.unit
class TestNavigationStrategyInterface:
    """Test that strategies implement the NavigationStrategy interface."""

    def test_mobile_strategy_implements_interface(self):
        """Test MobileNavigationStrategy implements all required methods."""
        strategy = MobileNavigationStrategy()
        assert isinstance(strategy, NavigationStrategy)
        assert hasattr(strategy, 'navigate_to_date')
        assert hasattr(strategy, 'wait_for_matrix_date')

    def test_desktop_strategy_implements_interface(self):
        """Test DesktopNavigationStrategy implements all required methods."""
        strategy = DesktopNavigationStrategy()
        assert isinstance(strategy, NavigationStrategy)
        assert hasattr(strategy, 'navigate_to_date')
        assert hasattr(strategy, 'wait_for_matrix_date')


@pytest.mark.unit
class TestParseMonthAbbreviation:
    """Test the parse_month_abbreviation helper function."""

    def test_english_abbreviations(self):
        """Test standard English month abbreviations."""
        assert parse_month_abbreviation("Jan") == 1
        assert parse_month_abbreviation("Feb") == 2
        assert parse_month_abbreviation("Mar") == 3
        assert parse_month_abbreviation("Apr") == 4
        assert parse_month_abbreviation("May") == 5
        assert parse_month_abbreviation("Jun") == 6
        assert parse_month_abbreviation("Jul") == 7
        assert parse_month_abbreviation("Aug") == 8
        assert parse_month_abbreviation("Sep") == 9
        assert parse_month_abbreviation("Oct") == 10
        assert parse_month_abbreviation("Nov") == 11
        assert parse_month_abbreviation("Dec") == 12

    def test_dutch_abbreviations(self):
        """Test Dutch month abbreviations."""
        assert parse_month_abbreviation("Maa") == 3   # Maart
        assert parse_month_abbreviation("Mrt") == 3   # Maart (alternative)
        assert parse_month_abbreviation("Mei") == 5   # Mei
        assert parse_month_abbreviation("Okt") == 10  # Oktober

    def test_uppercase_abbreviations(self):
        """Test that uppercase abbreviations are handled (e.g., 'MAA 2026')."""
        assert parse_month_abbreviation("MAA") == 3
        assert parse_month_abbreviation("JAN") == 1
        assert parse_month_abbreviation("OKT") == 10
        assert parse_month_abbreviation("MEI") == 5

    def test_lowercase_abbreviations(self):
        """Test that lowercase abbreviations are handled."""
        assert parse_month_abbreviation("jan") == 1
        assert parse_month_abbreviation("maa") == 3
        assert parse_month_abbreviation("dec") == 12

    def test_invalid_abbreviation_raises_value_error(self):
        """Test that an unrecognized abbreviation raises ValueError."""
        with pytest.raises(ValueError, match="is not in list"):
            parse_month_abbreviation("Xyz")

    def test_navigate_to_date_with_dutch_month(self):
        """Test that desktop navigation handles Dutch month abbreviations like 'MAA 2026'."""
        strategy = DesktopNavigationStrategy()

        mock_driver = Mock()
        mock_wait = Mock()
        mock_logger = Mock()

        # Mock calendar title showing MAA 2026 (Dutch for March 2026)
        mock_calendar_title = Mock()
        mock_calendar_title.text = "MAA 2026"

        mock_date_link = Mock()

        def mock_find_element(by, value):
            if value == "calendar_date_title":
                return mock_calendar_title
            return Mock()

        mock_driver.find_element.side_effect = mock_find_element

        wait_call_count = [0]

        def mock_until(condition):
            wait_call_count[0] += 1
            if wait_call_count[0] == 3:
                return mock_date_link
            return Mock()

        mock_wait.until.side_effect = mock_until

        # Navigate to a date in March 2026 - should not log any errors
        strategy.navigate_to_date(mock_driver, mock_wait, mock_logger, "2026-03-19")

        # Verify no error was logged for month parsing
        mock_logger.error.assert_not_called()
        # Verify date link was clicked
        mock_date_link.click.assert_called_once()
