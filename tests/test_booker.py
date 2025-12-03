"""Unit tests for PadelBooker class methods."""

import pytest
from unittest.mock import Mock, patch

from selenium.webdriver.support.ui import Select

from padel_booker.booker import PadelBooker


@pytest.mark.unit
class TestPadelBookerInit:
    """Test PadelBooker initialization."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_init_creates_booker(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test PadelBooker initializes correctly."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        booker = PadelBooker()

        assert booker.driver == mock_driver
        assert booker.wait == mock_wait
        mock_setup_driver.assert_called_once()
        mock_strategy_class.assert_called_once()
        mock_logging.assert_called_once()


@pytest.mark.unit
class TestPadelBookerCheckAvailability:
    """Test check_availability method."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_slot_found(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test when matching slot is found."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock slot element
        mock_slot = Mock()
        mock_period_div = Mock()
        mock_period_div.text = "21:30 - 23:00"
        mock_slot.find_element.return_value = mock_period_div

        mock_driver.find_elements.return_value = [mock_slot]

        result = booker.check_availability("2025-12-01", "21:30", 1.5)

        assert result == mock_slot

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_no_slot_found(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test when no matching slot is found."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock slot with different time
        mock_slot = Mock()
        mock_period_div = Mock()
        mock_period_div.text = "20:00 - 21:30"
        mock_slot.find_element.return_value = mock_period_div

        mock_driver.find_elements.return_value = [mock_slot]

        result = booker.check_availability("2025-12-01", "21:30", 1.5)

        assert result is None


@pytest.mark.unit
class TestPadelBookerSelectPlayers:
    """Test select_players method."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_select_three_players(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test selecting three players successfully."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock select elements for players 2, 3, 4
        mock_selects = []
        for i in range(3):
            mock_select_element = Mock()
            mock_option = Mock()
            mock_option.text = f"Player {i+2}"
            mock_select = Mock(spec=Select)
            mock_select.options = [mock_option]
            mock_selects.append((mock_select_element, mock_select))

        call_count = [0]

        def mock_find_element(by, value):
            if value.startswith("players["):
                idx = call_count[0]
                call_count[0] += 1
                return mock_selects[idx][0]
            return Mock()

        booker.driver.find_element = mock_find_element

        with patch("padel_booker.booker.Select", side_effect=[s[1] for s in mock_selects]):
            candidates = ["Player 2", "Player 3", "Player 4", "Player 5"]
            selected = booker.select_players(candidates)

            assert len(selected) == 3
            assert "Player 2" in selected
            assert "Player 3" in selected
            assert "Player 4" in selected


@pytest.mark.unit
class TestPadelBookerFindConsecutiveSlots:
    """Test find_consecutive_slots method."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_consecutive_slots_found(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test finding consecutive slots for duration."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Create mock slots
        mock_slot1 = Mock()
        mock_period1 = Mock()
        mock_period1.text = "21:00 - 22:00"
        mock_slot1.find_element.return_value = mock_period1
        mock_slot1.get_attribute.return_value = "Court 1"

        mock_slot2 = Mock()
        mock_period2 = Mock()
        mock_period2.text = "22:00 - 23:00"
        mock_slot2.find_element.return_value = mock_period2
        mock_slot2.get_attribute.return_value = "Court 1"

        mock_driver.find_elements.return_value = [mock_slot1, mock_slot2]

        slot, end_time = booker.find_consecutive_slots("21:00", 2.0)

        assert slot == mock_slot1
        assert end_time == "23:00"

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_no_consecutive_slots(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test when no consecutive slots are found."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Create mock slots that are not consecutive
        mock_slot1 = Mock()
        mock_period1 = Mock()
        mock_period1.text = "21:00 - 22:00"
        mock_slot1.find_element.return_value = mock_period1
        mock_slot1.get_attribute.return_value = "Court 1"

        mock_slot2 = Mock()
        mock_period2 = Mock()
        mock_period2.text = "23:00 - 00:00"  # Gap between slots
        mock_slot2.find_element.return_value = mock_period2
        mock_slot2.get_attribute.return_value = "Court 1"

        mock_driver.find_elements.return_value = [mock_slot1, mock_slot2]

        slot, end_time = booker.find_consecutive_slots("21:00", 2.0)

        assert slot is None
        assert end_time is None


@pytest.mark.unit
class TestPadelBookerContextManager:
    """Test PadelBooker context manager."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_context_manager_enter(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test context manager __enter__."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        result = booker.__enter__()
        assert result == booker

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_context_manager_exit(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test context manager __exit__ calls driver.quit()."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()
        booker.__exit__(None, None, None)

        mock_driver.quit.assert_called_once()


@pytest.mark.unit
class TestPadelBookerDelegation:
    """Test that PadelBooker delegates to navigation strategy."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_go_to_date_delegates_to_strategy(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test go_to_date delegates to navigation strategy."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        mock_strategy = Mock()
        mock_strategy_class.return_value = mock_strategy

        booker = PadelBooker()
        booker.go_to_date("2025-12-01")

        mock_strategy.navigate_to_date.assert_called_once()

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_wait_for_matrix_date_delegates_to_strategy(self, mock_logging, mock_setup_driver, mock_strategy_class):
        """Test wait_for_matrix_date delegates to navigation strategy."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        mock_strategy = Mock()
        mock_strategy_class.return_value = mock_strategy

        booker = PadelBooker()
        booker.wait_for_matrix_date("2025-12-01")

        mock_strategy.wait_for_matrix_date.assert_called_once()


@pytest.mark.unit
class TestPadelBookerBackwardsDaySearch:
    """Test backwards day search for workdays when slots not available."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_finds_slot_on_previous_workday_when_original_day_unavailable(
        self, mock_logging, mock_setup_driver, mock_strategy_class
    ):
        """Test that when slot not available on Friday, searches back to Thursday."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock slot on Thursday
        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # First call (Friday 2025-12-05) returns no slots
        # Second call (Thursday 2025-12-04) returns a slot
        mock_driver.find_elements.side_effect = [
            [],  # Friday - no slots
            [mock_slot],  # Thursday - has slot
        ]

        # Mock navigation methods
        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-05", "21:00", 2.0
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-04"
        # Should have navigated to Thursday after Friday failed
        assert booker.go_to_date.call_count == 2

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_skips_weekend_when_searching_backwards(
        self, mock_logging, mock_setup_driver, mock_strategy_class
    ):
        """Test that backwards search skips Saturday and Sunday."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock slot on Friday
        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Monday (no slots) -> skip Sat/Sun -> Friday (has slot)
        mock_driver.find_elements.side_effect = [
            [],  # Monday 2025-12-08 - no slots
            [mock_slot],  # Friday 2025-12-05 - has slot
        ]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-08", "21:00", 2.0
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-05"
        # Should have navigated to Monday and then Friday (skipping weekend)
        assert booker.go_to_date.call_count == 2

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_returns_none_when_no_slots_found_after_searching_backwards(
        self, mock_logging, mock_setup_driver, mock_strategy_class
    ):
        """Test returns None when no slots found after searching backwards."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # No slots on any day
        mock_driver.find_elements.return_value = []

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-05", "21:00", 2.0, max_days_back=3
        )

        assert slot is None
        assert end_time is None
        assert found_date is None
