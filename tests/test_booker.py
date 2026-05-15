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
class TestPadelBookerFallbackSearch:
    """Test fallback search avoiding Friday and weekends."""

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_finds_slot_on_target_date_when_available(
        self, mock_logging, mock_setup_driver, mock_strategy_class
    ):
        """Test that slot is found on target date if available (Monday-Thursday)."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock slot on Wednesday
        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Wednesday 2025-12-03 has slots
        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-03", "21:00", 2.0
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-03"
        # Should only navigate to the target date
        assert booker.go_to_date.call_count == 1

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_skips_friday_as_target_date(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that Friday target date is skipped and backward search begins."""
        from datetime import datetime as real_datetime
        
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock today as 2025-12-01 (before test dates)
        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        # Keep strptime working normally
        mock_datetime_class.strptime = real_datetime.strptime

        # Mock slot on Thursday (backward from Friday)
        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Friday is skipped, Thursday (backward) has slot
        # First call: Thursday 2025-12-04 (backward from Friday)
        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Friday 2025-12-05
        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-05", "21:00", 2.0
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-04"
        # Should navigate directly to Thursday (latest valid date before Friday) first
        assert booker.go_to_date.call_count == 1
        assert booker.go_to_date.call_args_list[0][0][0] == "2025-12-04"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_navigates_to_thursday_for_saturday_target(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that Saturday target date navigates directly to Thursday (latest valid date)."""
        from datetime import datetime as real_datetime

        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock today as 2025-12-01 (before test dates)
        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        mock_datetime_class.strptime = real_datetime.strptime

        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Saturday 2025-12-06 target: should navigate directly to Thursday 2025-12-04
        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-06", "21:00", 2.0
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-04"
        # Should navigate directly to Thursday (skipping Saturday and Friday)
        assert booker.go_to_date.call_count == 1
        assert booker.go_to_date.call_args_list[0][0][0] == "2025-12-04"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_searches_backward_only(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that backward search happens when target has no slots."""
        from datetime import datetime as real_datetime
        
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock today as 2025-12-01 (before test dates)
        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        # Keep strptime working normally
        mock_datetime_class.strptime = real_datetime.strptime

        # Mock slot on previous Tuesday
        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Wednesday target: no slots
        # Tuesday backward: has slot
        mock_driver.find_elements.side_effect = [
            [],  # Wednesday 2025-12-03 target - no slots
            [mock_slot],  # Tuesday 2025-12-02 backward - has slot
        ]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-03", "21:00", 2.0, max_days_back=2
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-02"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_skips_weekend_and_friday_when_searching(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that search skips Friday, Saturday and Sunday when searching backward."""
        from datetime import datetime as real_datetime
        
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock today as 2025-11-30 (before test dates)
        mock_today = real_datetime(2025, 11, 30).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        # Keep strptime working normally
        mock_datetime_class.strptime = real_datetime.strptime

        # Mock slot on previous Monday
        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Thursday target: no slots
        # Skip Wed, Tue, then previous Monday (backward) has slot
        mock_driver.find_elements.side_effect = [
            [],  # Thursday 2025-12-04 target - no slots
            [],  # Wednesday 2025-12-03 backward - no slots
            [],  # Tuesday 2025-12-02 backward - no slots
            [mock_slot],  # Monday 2025-12-01 backward - has slot
        ]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-04", "21:00", 2.0, max_days_back=3
        )

        assert slot == mock_slot
        assert end_time == "23:00"
        assert found_date == "2025-12-01"

    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_returns_none_when_no_slots_found_in_search_window(
        self, mock_logging, mock_setup_driver, mock_strategy_class
    ):
        """Test returns None when no slots found in search window."""
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # No slots on any day
        mock_driver.find_elements.return_value = []

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-03", "21:00", 2.0, max_days_back=3
        )

        assert slot is None
        assert end_time is None
        assert found_date is None

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_stops_backward_search_at_runtime_date(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that backward search stops when reaching the current runtime date."""
        from datetime import datetime as real_datetime
        
        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        # Mock today as 2025-12-01 (Monday)
        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        # Keep strptime working normally
        mock_datetime_class.strptime = real_datetime.strptime

        # No slots on any day
        mock_driver.find_elements.return_value = []

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Target date is Wednesday 2025-12-03 (2 days after today)
        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-03", "21:00", 2.0, max_days_back=10
        )

        # Should search Wednesday 2025-12-03 (target), Tuesday 2025-12-02 (backward), 
        # and Monday 2025-12-01 (today - backward), but NOT go before today
        assert booker.go_to_date.call_count == 3  # Wednesday, Tuesday, and Monday (today)
        assert slot is None
        assert end_time is None
        assert found_date is None
        
        # Verify the dates that were searched
        calls = [call[0][0] for call in booker.go_to_date.call_args_list]
        assert calls == ["2025-12-03", "2025-12-02", "2025-12-01"]


@pytest.mark.unit
class TestPadelBookerFallbackSearchNewOptions:
    """Test fallback search with skip_dates, skip_weekends, and conditional_skip_rules."""

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_skips_specific_date_in_skip_dates(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that a date listed in skip_dates is skipped and search moves to previous day."""
        from datetime import datetime as real_datetime

        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        mock_datetime_class.strptime = real_datetime.strptime

        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Wednesday 2025-12-03 is in skip_dates, so should navigate to Tuesday 2025-12-02
        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-03", "21:00", 2.0, skip_dates=["2025-12-03"]
        )

        assert slot == mock_slot
        assert found_date == "2025-12-02"
        assert booker.go_to_date.call_args_list[0][0][0] == "2025-12-02"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_skip_weekends_false_allows_friday(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that skip_weekends=False allows booking on Friday."""
        from datetime import datetime as real_datetime

        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        mock_datetime_class.strptime = real_datetime.strptime

        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Friday 2025-12-05 with skip_weekends=False: should use Friday directly
        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-05", "21:00", 2.0, skip_weekends=False
        )

        assert slot == mock_slot
        assert found_date == "2025-12-05"
        assert booker.go_to_date.call_args_list[0][0][0] == "2025-12-05"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_conditional_skip_rule_skips_thursday_before_date(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that a conditional rule skips Thursday before a cutoff date."""
        from datetime import datetime as real_datetime
        from types import SimpleNamespace

        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        mock_datetime_class.strptime = real_datetime.strptime

        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        # Thursday is skipped by rule; Wednesday is the first date navigated to and has slots
        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Rule: skip Thursday (weekday=3) before 2026-01-01
        rule = SimpleNamespace(weekday=3, before_date="2026-01-01", after_date=None)

        # Target is Thursday 2025-12-04, but rule skips it -> latest valid is Wed 2025-12-03
        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-04", "21:00", 2.0, conditional_skip_rules=[rule]
        )

        assert slot == mock_slot
        assert found_date == "2025-12-03"
        assert booker.go_to_date.call_args_list[0][0][0] == "2025-12-03"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_conditional_skip_rule_no_date_range_always_skips_weekday(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that a rule with no date conditions skips the weekday unconditionally."""
        from datetime import datetime as real_datetime
        from types import SimpleNamespace

        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        mock_today = real_datetime(2025, 12, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        mock_datetime_class.strptime = real_datetime.strptime

        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Rule: always skip Thursday (no date conditions)
        rule = SimpleNamespace(weekday=3, before_date=None, after_date=None)

        # Target is Thursday 2025-12-04; rule has no date range so Thursday is always skipped
        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2025-12-04", "21:00", 2.0, conditional_skip_rules=[rule]
        )

        assert slot == mock_slot
        assert found_date == "2025-12-03"  # Wednesday
        assert booker.go_to_date.call_args_list[0][0][0] == "2025-12-03"

    @patch("padel_booker.booker.datetime")
    @patch("padel_booker.booker.DesktopNavigationStrategy")
    @patch("padel_booker.booker.setup_driver")
    @patch("padel_booker.booker.setup_logging")
    def test_conditional_skip_rule_allows_thursday_after_cutoff(
        self, mock_logging, mock_setup_driver, mock_strategy_class, mock_datetime_class
    ):
        """Test that Thursday after the before_date cutoff is allowed."""
        from datetime import datetime as real_datetime
        from types import SimpleNamespace

        mock_driver = Mock()
        mock_wait = Mock()
        mock_setup_driver.return_value = (mock_driver, mock_wait)

        booker = PadelBooker()

        mock_today = real_datetime(2026, 1, 1).date()
        mock_datetime_class.now.return_value.date.return_value = mock_today
        mock_datetime_class.strptime = real_datetime.strptime

        mock_slot = Mock()
        mock_period = Mock()
        mock_period.text = "21:00 - 23:00"
        mock_slot.find_element.return_value = mock_period
        mock_slot.get_attribute.return_value = "Court 1"

        mock_driver.find_elements.return_value = [mock_slot]

        booker.go_to_date = Mock()
        booker.wait_for_matrix_date = Mock()

        # Rule: skip Thursday before 2026-01-01; target is Thursday 2026-01-01 (at cutoff, not before)
        rule = SimpleNamespace(weekday=3, before_date="2026-01-01", after_date=None)

        slot, end_time, found_date = booker.find_consecutive_slots_with_fallback(
            "2026-01-01", "21:00", 2.0, conditional_skip_rules=[rule]
        )

        assert slot == mock_slot
        assert found_date == "2026-01-01"
        assert booker.go_to_date.call_args_list[0][0][0] == "2026-01-01"
