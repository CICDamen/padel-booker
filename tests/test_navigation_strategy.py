"""Unit tests for navigation strategies."""

import pytest
from unittest.mock import Mock, patch

from padel_booker.navigation_strategy import (
    NavigationStrategy,
    DesktopNavigationStrategy,
    MobileNavigationStrategy,
    get_navigation_strategy
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

        # Mock date cell and link
        mock_date_cell = Mock()
        mock_date_link = Mock()
        mock_date_cell.find_element.return_value = mock_date_link

        def mock_find_element(by, value):
            if value == "calendar_date_title":
                return mock_calendar_title
            elif value.startswith("cal_"):
                return mock_date_cell
            return Mock()

        mock_driver.find_element.side_effect = mock_find_element

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
