"""
Tests for task API routes.

Note:
This test file was generated with assistance from an AI tool (ChatGPT)
and reviewed/edited by the project author before submission.
"""

import pytest
from unittest.mock import patch


class DummyTask:
    """
    Simple mock task object used to simulate service layer return values.
    """
    def __init__(self, task_id=1, title="test task"):
        self.task_id = task_id
        self.title = title

    def to_dict(self):
        return {
            "id": self.task_id,
            "title": self.title
        }


def test_create_task_success(client):
    """
    Test successful task creation.

    The route should return:
    - HTTP 201 status
    - JSON representation of the created task
    """
    payload = {"title": "test task"}

    with patch("modules.tasks.service.create_task", return_value=DummyTask()):
        response = client.post("/tasks", json=payload)

    assert response.status_code == 201

    data = response.get_json()
    assert data["title"] == "test task"


def test_create_task_validation_error(client):
    """
    Test task creation when validation fails.

    If the service layer raises ValueError, the route
    should return HTTP 400 with an error message.
    """
    with patch(
        "modules.tasks.service.create_task",
        side_effect=ValueError("invalid task")
    ):
        response = client.post("/tasks", json={})

    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data


def test_get_task_success(client):
    """
    Test retrieving a task by id.
    """
    with patch(
        "modules.tasks.service.get_task",
        return_value=DummyTask(task_id=1)
    ):
        response = client.get("/tasks/1")

    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == 1


def test_delete_task_success(client):
    """
    Test soft deleting a task.

    The endpoint should return status OK when deletion succeeds.
    """
    with patch("modules.tasks.service.soft_delete_task", return_value=None):
        response = client.patch("/tasks/1/delete")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_restore_task_success(client):
    """
    Test restoring a previously deleted task.
    """
    with patch("modules.tasks.service.restore_task", return_value=None):
        response = client.patch("/tasks/1/restore")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_list_tasks(client):
    """
    Test listing tasks.

    The endpoint should return a list of task dictionaries.
    """
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

