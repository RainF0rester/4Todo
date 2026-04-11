import pytest
from unittest.mock import MagicMock, patch
from modules.tasks import service


def valid_payload():
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1,
        "is_finished": 0,
    }


def test_create_task_success():
    with patch("modules.tasks.repo.create_task") as mock_create:
        mock_task = MagicMock()
        mock_create.return_value = mock_task

        result = service.create_task(None, valid_payload(), user_id=1)

        assert result == mock_task
        mock_create.assert_called_once()
        created_task = mock_create.call_args[0][1]
        assert created_task.user_id == 1
        assert created_task.task_title == "test task"
        assert created_task.task_due == "2099-01-01 10:30:00"


def test_create_task_rejects_invalid_payload():
    with pytest.raises(ValueError):
        service.create_task(None, {"task_title": "   "}, user_id=1)