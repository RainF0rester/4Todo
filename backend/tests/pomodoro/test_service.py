import pytest
from unittest.mock import MagicMock, patch
from backend.modules.pomodoro import service


def test_log_pomodoro_calls_upsert_with_today():
    with patch("backend.modules.pomodoro.repo.upsert_pomodoro") as mock_upsert:
        mock_record = MagicMock()
        mock_upsert.return_value = mock_record

        result = service.log_pomodoro(None, user_id=1)

        assert result == mock_record
        mock_upsert.assert_called_once()
        _, called_user_id, called_date = mock_upsert.call_args[0]
        assert called_user_id == 1
        from datetime import date
        assert called_date == date.today().isoformat()


def test_get_today_returns_record():
    with patch("backend.modules.pomodoro.repo.get_by_date") as mock_get:
        mock_record = MagicMock()
        mock_get.return_value = mock_record

        result = service.get_today(None, user_id=1)

        assert result == mock_record
        mock_get.assert_called_once()


def test_get_today_returns_none_when_no_record():
    with patch("backend.modules.pomodoro.repo.get_by_date", return_value=None):
        result = service.get_today(None, user_id=1)
        assert result is None


def test_get_range_success():
    with patch("backend.modules.pomodoro.repo.list_by_range") as mock_list:
        mock_list.return_value = [MagicMock(), MagicMock()]
        result = service.get_range(None, user_id=1, start_date="2026-01-01", end_date="2026-01-31")
        assert len(result) == 2
        mock_list.assert_called_once_with(None, 1, "2026-01-01", "2026-01-31")


def test_get_range_rejects_start_after_end():
    with pytest.raises(ValueError, match="start_date must be before end_date"):
        service.get_range(None, user_id=1, start_date="2026-02-01", end_date="2026-01-01")


def test_get_range_rejects_invalid_start_date():
    with pytest.raises(ValueError, match="Invalid date format"):
        service.get_range(None, user_id=1, start_date="not-a-date", end_date="2026-01-31")


def test_get_range_rejects_invalid_end_date():
    with pytest.raises(ValueError, match="Invalid date format"):
        service.get_range(None, user_id=1, start_date="2026-01-01", end_date="31-01-2026")


def test_get_range_accepts_same_start_and_end():
    with patch("backend.modules.pomodoro.repo.list_by_range") as mock_list:
        mock_list.return_value = []
        result = service.get_range(None, user_id=1, start_date="2026-01-01", end_date="2026-01-01")
        assert result == []
