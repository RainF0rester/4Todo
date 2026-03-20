import pytest
from unittest.mock import patch


class DummyTask:
    def __init__(self, task_id=1, task_title="test task"):
        self.task_id = task_id
        self.task_title = task_title

    def to_dict(self):
        return {
            "id": self.task_id,
            "task_title": self.task_title,
            "task_due": None,
            "task_description": None,
            "task_level": 1,
            "is_finished": 0
        }


def valid_payload():
    return {
        "task_title": "test task",
        "task_due": "2026-01-01",
        "task_description": "test desc",
        "task_level": 1
    }


def test_create_task_success(client):
    with patch("modules.tasks.service.create_task", return_value=DummyTask()):
        response = client.post("/tasks", json=valid_payload())

    assert response.status_code == 201

    data = response.get_json()
    assert data["task_title"] == "test task"


def test_create_task_validation_error(client):
    with patch(
        "modules.tasks.service.create_task",
        side_effect=ValueError("invalid task")
    ):
        response = client.post("/tasks", json=valid_payload())

    assert response.status_code == 400

    data = response.get_json()
    assert "message" in data


def test_get_task_success(client):
    with patch(
        "modules.tasks.service.get_task",
        return_value=DummyTask(task_id=1)
    ):
        response = client.get("/tasks/1")

    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == 1


def test_delete_task_success(client):
    with patch("modules.tasks.service.soft_delete_task", return_value=None):
        response = client.patch("/tasks/1/delete")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_restore_task_success(client):
    with patch("modules.tasks.service.restore_task", return_value=None):
        response = client.patch("/tasks/1/restore")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_list_tasks(client):
    tasks = [
        DummyTask(task_id=1),
        DummyTask(task_id=2)
    ]

    with patch("modules.tasks.service.list_tasks", return_value=tasks):
        response = client.get("/tasks")

    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2