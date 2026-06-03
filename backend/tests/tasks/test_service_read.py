import pytest
from unittest.mock import MagicMock, patch
from backend.modules.tasks import service


def make_task(task_id=1, user_id=1, is_deleted=0):
    task = MagicMock()
    task.id = task_id
    task.user_id = user_id
    task.is_deleted = is_deleted
    return task


def test_get_task_success():
    fake_task = make_task(task_id=1, user_id=1, is_deleted=0)

    with patch("backend.modules.tasks.repo.get_task", return_value=fake_task):
        result = service.get_task(None, 1, user_id=1)
        assert result == fake_task


def test_get_task_not_found():
    with patch("backend.modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError, match="Task not found"):
            service.get_task(None, 1, user_id=1)


def test_get_task_rejects_deleted_task():
    fake_task = make_task(task_id=1, user_id=1, is_deleted=1)

    with patch("backend.modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError, match="Task not found"):
            service.get_task(None, 1, user_id=1)


def test_get_task_rejects_task_from_other_user():
    fake_task = make_task(task_id=1, user_id=2, is_deleted=0)

    with patch("backend.modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError, match="Task not found"):
            service.get_task(None, 1, user_id=1)


def test_list_tasks_returns_active_tasks():
    fake_list = [MagicMock(), MagicMock()]

    with patch("backend.modules.tasks.repo.list_tasks", return_value=fake_list) as mock_list:
        result = service.list_tasks(None, user_id=1)

        assert result == fake_list
        mock_list.assert_called_once_with(None, user_id=1, include_deleted=False)


def test_list_tasks_include_deleted_passes_flag_to_repo():
    fake_list = [MagicMock()]

    with patch("backend.modules.tasks.repo.list_tasks", return_value=fake_list) as mock_list:
        result = service.list_tasks(None, user_id=1, include_deleted=True)

        assert result == fake_list
        mock_list.assert_called_once_with(None, user_id=1, include_deleted=True)