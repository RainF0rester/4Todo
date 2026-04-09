import pytest
from unittest.mock import MagicMock, patch
from modules.tasks import service


# ============================================================
# get_task
# These tests verify reading a single task through the service layer.
# The service should reject missing or soft-deleted tasks.
# ============================================================

def test_get_task_success():
    """
    A non-deleted existing task should be returned successfully.
    """
    fake_task = MagicMock()
    fake_task.is_deleted = 0

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        result = service.get_task(None, 1)
        assert result == fake_task


def test_get_task_not_found():
    """
    Requesting a task that does not exist should raise a ValueError.
    """
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError):
            service.get_task(None, 1)


def test_get_task_rejects_deleted_task():
    """
    Soft-deleted tasks should not be returned as normal active tasks.
    """
    fake_task = MagicMock()
    fake_task.is_deleted = 1

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError):
            service.get_task(None, 1)


# ============================================================
# list_tasks
# These tests verify task list retrieval through the service layer.
# ============================================================

def test_list_tasks_returns_active_tasks():
    """
    The service should return the list produced by the repo layer.
    """
    fake_list = [MagicMock(), MagicMock()]

    with patch("modules.tasks.repo.list_tasks", return_value=fake_list):
        result = service.list_tasks(None)

        assert result == fake_list


def test_list_tasks_include_deleted_passes_flag_to_repo():
    """
    When include_deleted=True is requested, the service should forward
    that option to the repo layer correctly.
    """
    fake_list = [MagicMock()]

    with patch("modules.tasks.repo.list_tasks", return_value=fake_list) as mock_list:
        result = service.list_tasks(None, include_deleted=True)

        assert result == fake_list
        mock_list.assert_called_once_with(None, include_deleted=True)