"""Tests for the PadelBooker class with mocked Selenium."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime

from src.padel_booker.booker import PadelBooker
from src.padel_booker.exceptions import PlayerSelectionExhaustedError


class TestPadelBookerInit:
    """Tests for PadelBooker initialization."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_init_creates_logger_and_driver(self, mock_logging, mock_driver):
        """Test that initialization creates logger and driver."""
        mock_logger = MagicMock()
        mock_logging.return_value = mock_logger
        mock_driver.return_value = (MagicMock(), MagicMock())

        booker = PadelBooker()

        mock_logging.assert_called_once_with("padel_booker")
        mock_driver.assert_called_once()
        assert booker.logger == mock_logger

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_context_manager_entry(self, mock_logging, mock_driver):
        """Test that context manager entry returns self."""
        mock_driver.return_value = (MagicMock(), MagicMock())

        booker = PadelBooker()
        result = booker.__enter__()

        assert result is booker

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_context_manager_exit_quits_driver(self, mock_logging, mock_driver):
        """Test that context manager exit quits the driver."""
        mock_driver_instance = MagicMock()
        mock_driver.return_value = (mock_driver_instance, MagicMock())

        booker = PadelBooker()
        booker.__exit__(None, None, None)

        mock_driver_instance.quit.assert_called_once()


class TestPadelBookerLogin:
    """Tests for PadelBooker login method."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_login_success(self, mock_logging, mock_driver):
        """Test successful login."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        # Mock the elements
        mock_username_field = MagicMock()
        mock_password_field = MagicMock()
        mock_login_button = MagicMock()

        def find_element_side_effect(by, value):
            if value == "username":
                return mock_username_field
            elif value == "password":
                return mock_password_field
            elif value == "#login-form button":
                return mock_login_button
            return MagicMock()

        mock_driver_instance.find_element.side_effect = find_element_side_effect

        booker = PadelBooker()
        result = booker.login("user", "pass", "https://example.com")

        assert result is True
        mock_driver_instance.get.assert_called_once_with("https://example.com")
        mock_username_field.send_keys.assert_called_once_with("user")
        mock_password_field.send_keys.assert_called_once_with("pass")
        mock_login_button.click.assert_called_once()

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_login_failure(self, mock_logging, mock_driver):
        """Test login failure when element not found."""
        from selenium.common.exceptions import NoSuchElementException

        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        mock_driver_instance.find_element.side_effect = NoSuchElementException()

        booker = PadelBooker()
        result = booker.login("user", "pass", "https://example.com")

        assert result is False


class TestPadelBookerCheckAvailability:
    """Tests for PadelBooker check_availability method."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_check_availability_finds_slot(self, mock_logging, mock_driver):
        """Test that check_availability finds matching slot."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        # Create mock slot element
        mock_slot = MagicMock()
        mock_period_div = MagicMock()
        mock_period_div.text = "21:30 - 23:00"
        mock_slot.find_element.return_value = mock_period_div

        mock_driver_instance.find_elements.return_value = [mock_slot]

        booker = PadelBooker()
        result = booker.check_availability("2025-07-28", "21:30", 1.5)

        assert result is mock_slot

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_check_availability_no_matching_slot(self, mock_logging, mock_driver):
        """Test that check_availability returns None when no matching slot."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        # Create mock slot element with wrong time
        mock_slot = MagicMock()
        mock_period_div = MagicMock()
        mock_period_div.text = "20:00 - 21:30"
        mock_slot.find_element.return_value = mock_period_div

        mock_driver_instance.find_elements.return_value = [mock_slot]

        booker = PadelBooker()
        result = booker.check_availability("2025-07-28", "21:30", 1.5)

        assert result is None


class TestPadelBookerSelectPlayers:
    """Tests for PadelBooker select_players method."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_select_players_success(self, mock_logging, mock_driver):
        """Test successful player selection."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        # Create mock select elements for players 2, 3, 4
        def create_mock_select(player_idx):
            mock_select_elem = MagicMock()
            mock_option1 = MagicMock()
            mock_option1.text = "John Smith"
            mock_option2 = MagicMock()
            mock_option2.text = "Jane Doe"
            mock_option3 = MagicMock()
            mock_option3.text = "Mike Johnson"

            # Mock the select element to return options
            return mock_select_elem

        def find_element_side_effect(by, value):
            mock_select_elem = MagicMock()
            return mock_select_elem

        mock_driver_instance.find_element.side_effect = find_element_side_effect

        with patch("src.padel_booker.booker.Select") as mock_select_class:
            mock_select = MagicMock()
            mock_option1 = MagicMock()
            mock_option1.text.strip.return_value = "John Smith"
            mock_option2 = MagicMock()
            mock_option2.text.strip.return_value = "Jane Doe"
            mock_option3 = MagicMock()
            mock_option3.text.strip.return_value = "Mike Johnson"
            mock_select.options = [mock_option1, mock_option2, mock_option3]
            mock_select_class.return_value = mock_select

            booker = PadelBooker()
            result = booker.select_players(["John Smith", "Jane Doe", "Mike Johnson"])

            assert len(result) == 3
            assert "John Smith" in result
            assert "Jane Doe" in result
            assert "Mike Johnson" in result


class TestPadelBookerFindConsecutiveSlots:
    """Tests for PadelBooker find_consecutive_slots method."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_find_consecutive_slots_success(self, mock_logging, mock_driver):
        """Test finding consecutive slots successfully."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        # Create mock slots for consecutive booking
        mock_slot1 = MagicMock()
        mock_period_div1 = MagicMock()
        mock_period_div1.text = "21:30 - 22:30"
        mock_slot1.find_element.return_value = mock_period_div1
        mock_slot1.get_attribute.return_value = "Padel indoor 1"

        mock_slot2 = MagicMock()
        mock_period_div2 = MagicMock()
        mock_period_div2.text = "22:30 - 23:30"
        mock_slot2.find_element.return_value = mock_period_div2
        mock_slot2.get_attribute.return_value = "Padel indoor 1"

        mock_driver_instance.find_elements.return_value = [mock_slot1, mock_slot2]

        booker = PadelBooker()
        slot, end_time = booker.find_consecutive_slots("21:30", 2.0)

        # Should find consecutive slots on the same court
        assert slot is mock_slot1
        assert end_time == "23:30"

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    def test_find_consecutive_slots_no_match(self, mock_logging, mock_driver):
        """Test that no consecutive slots returns None."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        mock_driver_instance.find_elements.return_value = []

        booker = PadelBooker()
        slot, end_time = booker.find_consecutive_slots("21:30", 1.5)

        assert slot is None
        assert end_time is None


class TestPadelBookerGoToDate:
    """Tests for PadelBooker go_to_date method."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    @patch("src.padel_booker.booker.time.sleep")
    def test_go_to_date_same_month(self, mock_sleep, mock_logging, mock_driver):
        """Test navigating to a date in the current month."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        # Mock calendar title showing correct month
        mock_title = MagicMock()
        mock_title.text = "Jul 2025"

        # Mock date cell
        mock_date_cell = MagicMock()
        mock_date_link = MagicMock()
        mock_date_cell.find_element.return_value = mock_date_link

        def find_element_side_effect(by, value):
            if value == "calendar_date_title":
                return mock_title
            elif value == "cal_2025_7_28":
                return mock_date_cell
            return MagicMock()

        mock_driver_instance.find_element.side_effect = find_element_side_effect

        booker = PadelBooker()
        booker.go_to_date("2025-07-28")

        mock_date_link.click.assert_called_once()


class TestPadelBookerTryBookingWithPlayerRotation:
    """Tests for PadelBooker try_booking_with_player_rotation method."""

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    @patch("src.padel_booker.booker.is_booking_enabled")
    @patch("src.padel_booker.booker.time.sleep")
    def test_try_booking_success(self, mock_sleep, mock_booking_enabled, mock_logging, mock_driver):
        """Test successful booking with player rotation."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)
        mock_booking_enabled.return_value = False

        # Mock the verder button
        mock_verder_btn = MagicMock()

        # Mock no alert present - need to raise NoAlertPresentException on access
        from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException

        # Configure the switch_to.alert to raise the exception
        mock_alert = MagicMock()
        mock_alert.text = None
        type(mock_driver_instance.switch_to).alert = PropertyMock(side_effect=NoAlertPresentException())

        # Mock no popup
        def find_element_side_effect(by, value):
            if value == "__make_submit":
                return mock_verder_btn
            elif value == "swal2-popup":
                raise NoSuchElementException()
            return MagicMock()

        mock_driver_instance.find_element.side_effect = find_element_side_effect

        with patch.object(PadelBooker, "select_players", return_value=["Player1", "Player2", "Player3"]):
            booker = PadelBooker()
            result = booker.try_booking_with_player_rotation(
                ["Player1", "Player2", "Player3", "Player4"],
                "John"
            )

            assert result == ["Player1", "Player2", "Player3"]

    @patch("src.padel_booker.booker.setup_driver")
    @patch("src.padel_booker.booker.setup_logging")
    @patch("src.padel_booker.booker.time.sleep")
    @patch.dict("os.environ", {"MAX_BOOKING_ATTEMPTS": "2"})
    def test_try_booking_not_enough_players(self, mock_sleep, mock_logging, mock_driver):
        """Test booking fails when not enough players can be selected."""
        mock_driver_instance = MagicMock()
        mock_wait = MagicMock()
        mock_driver.return_value = (mock_driver_instance, mock_wait)

        with patch.object(PadelBooker, "select_players", return_value=["Player1", "Player2"]):
            booker = PadelBooker()

            with pytest.raises(PlayerSelectionExhaustedError):
                booker.try_booking_with_player_rotation(
                    ["Player1", "Player2"],
                    "John"
                )
