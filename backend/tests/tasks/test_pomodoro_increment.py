import pytest
from unittest.mock import MagicMock, patch
from backend.modules.tasks import service


def _dummy_task(task_id=1, user_id=1, pomodoro_count=0, is_deleted=0):
    task = MagicMock()
    task.id = task_id
    task.user_id = user_id
    task.pomodoro_count = pomodoro_count
    task.is_deleted = is_deleted
    return task


def _auth_patch():
    return patch(
        "backend.utils.auth_decorator.validate_token",
        return_value={"state": "active", "payload": {"user_id": 1}},
    )


# =========================
# Service
# =========================

def test_increment_pomodoro_success():
    task = _dummy_task(pomodoro_count=0)
    with patch("backend.modules.tasks.repo.get_task", return_value=task), \
         patch("backend.modules.tasks.repo.increment_pomodoro") as mock_inc:
        mock_inc.return_value = task
        result = service.increment_pomodoro(None, task_id=1, user_id=1)
        assert result == task
        mock_inc.assert_called_once_with(None, task)


def test_increment_pomodoro_rejects_missing_task():
    with patch("backend.modules.tasks.repo.get_task", return_value=None):
        with pytest.raises(ValueError, match="Task not found"):
            service.increment_pomodoro(None, task_id=999, user_id=1)


def test_increment_pomodoro_rejects_deleted_task():
    task = _dummy_task(is_deleted=1)
    with patch("backend.modules.tasks.repo.get_task", return_value=task):
        with pytest.raises(ValueError, match="Task not found"):
            service.increment_pomodoro(None, task_id=1, user_id=1)


def test_increment_pomodoro_rejects_wrong_user():
    task = _dummy_task(user_id=2)
    with patch("backend.modules.tasks.repo.get_task", return_value=task):
        with pytest.raises(ValueError, match="Task not found"):
            service.increment_pomodoro(None, task_id=1, user_id=1)


# =========================
# Route  PATCH /tasks/<id>/pomodoro
# =========================

def test_increment_pomodoro_route_success(client):
    mock_task = MagicMock()
    mock_task.to_dict.return_value = {
        "id": 1, "task_title": "test", "pomodoro_count": 1,
        "task_due": None, "task_description": None,
        "task_level": 0, "is_finished": 0, "is_pinned": 0,
        "user_id": 1, "is_deleted": 0, "scheduled_delete_time": None,
        "created_at": "2026-01-01", "updated_at": "2026-01-01",
    }
    with _auth_patch(), patch("backend.modules.tasks.service.increment_pomodoro") as mock_inc:
        mock_inc.return_value = mock_task
        resp = client.patch("/tasks/1/pomodoro", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 200
        assert resp.get_json()["pomodoro_count"] == 1


def test_increment_pomodoro_route_task_not_found(client):
    with _auth_patch(), patch("backend.modules.tasks.service.increment_pomodoro") as mock_inc:
        mock_inc.side_effect = ValueError("Task not found")
        resp = client.patch("/tasks/999/pomodoro", headers={"Authorization": "Bearer token"})
        assert resp.status_code == 400


def test_increment_pomodoro_route_requires_auth(client):
    resp = client.patch("/tasks/1/pomodoro")
    assert resp.status_code == 401
