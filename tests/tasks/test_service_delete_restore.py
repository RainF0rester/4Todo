import pytest
from unittest.mock import MagicMock, patch
from modules.tasks import service


def make_task(task_id=1, user_id=1, is_deleted=0):
    task = MagicMock()
    task.id = task_id
    task.user_id = user_id
    task.is_deleted = is_deleted
    return task


def test_soft_delete_task_success():
    task = make_task(task_id=1, user_id=1, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=task), \
         patch("modules.tasks.repo.soft_delete_task", return_value=True):
        service.soft_delete_task(None, 1, user_id=1)


def test_soft_delete_task_repo_failure():
    task = make_task(task_id=1, user_id=1, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=task), \
         patch("modules.tasks.repo.soft_delete_task", return_value=False):
        with pytest.raises(ValueError, match="Task failed to delete"):
            service.soft_delete_task(None, 1, user_id=1)


def test_soft_delete_task_not_found():
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError, match="Task not found"):
            service.soft_delete_task(None, 1, user_id=1)


def test_soft_delete_task_wrong_user():
    task = make_task(task_id=1, user_id=2, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=task):
        with pytest.raises(ValueError, match="Task not found"):
            service.soft_delete_task(None, 1, user_id=1)


def test_soft_delete_task_already_deleted():
    task = make_task(task_id=1, user_id=1, is_deleted=1)

    with patch("modules.tasks.repo.get_task", return_value=task):
        with pytest.raises(ValueError, match="Task not found"):
            service.soft_delete_task(None, 1, user_id=1)


def test_restore_task_success():
    task = make_task(task_id=1, user_id=1, is_deleted=1)

    with patch("modules.tasks.repo.get_task", return_value=task), \
         patch("modules.tasks.repo.restore_task", return_value=True):
        service.restore_task(None, 1, user_id=1)


def test_restore_task_repo_failure():
    task = make_task(task_id=1, user_id=1, is_deleted=1)

    with patch("modules.tasks.repo.get_task", return_value=task), \
         patch("modules.tasks.repo.restore_task", return_value=False):
        with pytest.raises(ValueError, match="Task failed to restore"):
            service.restore_task(None, 1, user_id=1)


def test_restore_task_not_found():
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError, match="Task not found"):
            service.restore_task(None, 1, user_id=1)


def test_restore_task_wrong_user():
    task = make_task(task_id=1, user_id=2, is_deleted=1)

    with patch("modules.tasks.repo.get_task", return_value=task):
        with pytest.raises(ValueError, match="Task not found"):
            service.restore_task(None, 1, user_id=1)


def test_restore_task_active_task_rejected():
    task = make_task(task_id=1, user_id=1, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=task):
        with pytest.raises(ValueError, match="Task not found"):
            service.restore_task(None, 1, user_id=1)