import pytest
from unittest.mock import MagicMock, patch
from modules.tasks import service


def valid_payload():
    """
    Return a valid task payload for create-task tests.
    """
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1,
        "is_finished": 0,
    }


# ============================================================
# create_task
# These tests focus on the create flow in the service layer:
# 1. validate and normalize input
# 2. delegate persistence to the repo layer
# ============================================================

def test_create_task_success():
    """
    A valid payload should be normalized and passed to the repo layer,
    and the created task object should be returned.
    """
    with patch("modules.tasks.repo.create_task") as mock_create:
        mock_task = MagicMock()
        mock_create.return_value = mock_task

        result = service.create_task(None, valid_payload())

        assert result == mock_task
        mock_create.assert_called_once()


def test_create_task_rejects_invalid_payload():
    """
    Invalid create payloads should fail before reaching the repo layer.
    """
    with pytest.raises(ValueError):
        service.create_task(None, {"task_title": "   "})