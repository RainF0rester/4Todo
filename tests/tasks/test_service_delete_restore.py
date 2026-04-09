import pytest
from unittest.mock import patch
from modules.tasks import service


# ============================================================
# soft_delete_task
# These tests verify soft deletion behavior in the service layer.
# ============================================================

def test_soft_delete_task_success():
    """
    If the repo layer reports success, the service should complete
    without raising an exception.
    """
    with patch("modules.tasks.repo.soft_delete_task", return_value=True):
        service.soft_delete_task(None, 1)


def test_soft_delete_task_not_found():
    """
    If the repo layer reports failure, the service should treat it as
    a missing task and raise ValueError.
    """
    with patch("modules.tasks.repo.soft_delete_task", return_value=False):
        with pytest.raises(ValueError):
            service.soft_delete_task(None, 1)


# ============================================================
# restore_task
# These tests verify restore behavior for previously deleted tasks.
# ============================================================

def test_restore_task_success():
    """
    A successful restore operation should complete without errors.
    """
    with patch("modules.tasks.repo.restore_task", return_value=True):
        service.restore_task(None, 1)


def test_restore_task_not_found():
    """
    If restore fails because the task does not exist (or cannot be restored),
    the service should raise ValueError.
    """
    with patch("modules.tasks.repo.restore_task", return_value=False):
        with pytest.raises(ValueError):
            service.restore_task(None, 1)