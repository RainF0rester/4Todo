import pytest
from unittest.mock import MagicMock, patch
from backend.modules.tasks import service


def make_task(task_id=1, user_id=1, is_deleted=0):
    task = MagicMock()
    task.id = task_id
    task.user_id = user_id
    task.is_deleted = is_deleted
    return task


def test_update_task_success():
    fake_task = make_task(task_id=1, user_id=1, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=fake_task), \
         patch("modules.tasks.repo.update_task", return_value=fake_task):

        result = service.update_task(None, 1, {"task_title": "new"}, user_id=1)

        assert result == fake_task
        assert fake_task.task_title == "new"


def test_update_task_rejects_missing_task():
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError, match="Task not found"):
            service.update_task(None, 1, {"task_title": "new"}, user_id=1)


def test_update_task_rejects_deleted_task():
    fake_task = make_task(task_id=1, user_id=1, is_deleted=1)

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError, match="Task not found"):
            service.update_task(None, 1, {"task_title": "new"}, user_id=1)


def test_update_task_rejects_task_from_other_user():
    fake_task = make_task(task_id=1, user_id=2, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError, match="Task not found"):
            service.update_task(None, 1, {"task_title": "new"}, user_id=1)


def test_update_task_rejects_empty_payload():
    fake_task = make_task(task_id=1, user_id=1, is_deleted=0)

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError, match="No fields to update"):
            service.update_task(None, 1, {}, user_id=1)