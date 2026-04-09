import pytest
from unittest.mock import MagicMock, patch
from modules.tasks import service


# ============================================================
# update_task
# These tests verify the service logic for updating tasks:
# 1. target task must exist
# 2. target task must not be deleted
# 3. update payload must not be empty
# 4. normalized fields should be applied before repo update
# ============================================================

def test_update_task_success():
    """
    A valid update should modify the task and return the updated object.
    """
    fake_task = MagicMock()
    fake_task.is_deleted = 0

    with patch("modules.tasks.repo.get_task", return_value=fake_task), \
         patch("modules.tasks.repo.update_task", return_value=fake_task):

        result = service.update_task(None, 1, {"task_title": "new"})

        assert result == fake_task
        assert fake_task.task_title == "new"


def test_update_task_rejects_missing_task():
    """
    Updating a non-existent task should raise a ValueError.
    """
    with patch("modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError):
            service.update_task(None, 1, {"task_title": "new"})


def test_update_task_rejects_deleted_task():
    """
    Deleted tasks should not be updated through the normal update flow.
    """
    fake_task = MagicMock()
    fake_task.is_deleted = 1

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError):
            service.update_task(None, 1, {"task_title": "new"})


def test_update_task_rejects_empty_payload():
    """
    An empty update payload should be rejected because there is nothing to update.
    """
    fake_task = MagicMock()
    fake_task.is_deleted = 0

    with patch("modules.tasks.repo.get_task", return_value=fake_task):
        with pytest.raises(ValueError):
            service.update_task(None, 1, {})