import pytest
from unittest.mock import patch


class DummyTask:
    def __init__(
        self,
        task_id=1,
        task_title="test task",
        task_due="2099-01-01 10:30",
        task_description=None,
        task_level=1,
        is_finished=0
    ):
        self.task_id = task_id
        self.task_title = task_title
        self.task_due = task_due
        self.task_description = task_description
        self.task_level = task_level
        self.is_finished = is_finished

    def to_dict(self):
        return {
            "id": self.task_id,
            "task_title": self.task_title,
            "task_due": self.task_due,
            "task_description": self.task_description,
            "task_level": self.task_level,
            "is_finished": self.is_finished,
        }


def valid_payload():
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1
    }


# =========================
# CREATE
# =========================

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
    assert "message" in response.get_json()


def test_create_task_invalid_due_format(client):
    payload = valid_payload()
    payload["task_due"] = "2099-01-01"

    with patch(
        "modules.tasks.service.create_task",
        side_effect=ValueError("Task due time must be in format YYYY-MM-DD HH:MM")
    ):
        response = client.post("/tasks", json=payload)

    assert response.status_code == 400


def test_create_task_past_due_time(client):
    payload = valid_payload()
    payload["task_due"] = "2020-01-01 10:30"

    with patch(
        "modules.tasks.service.create_task",
        side_effect=ValueError("Task due time cannot be in the past")
    ):
        response = client.post("/tasks", json=payload)

    assert response.status_code == 400


# def test_create_task_due_none(client):
#     payload = valid_payload()
#     payload["task_due"] = None
#
#     response = client.post("/tasks", json=payload)
#
#     assert response.status_code == 422


# =========================
# GET
# =========================

def test_get_task_success(client):
    with patch(
        "modules.tasks.service.get_task",
        return_value=DummyTask(task_id=1)
    ):
        response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_task_not_found(client):
    with patch(
        "modules.tasks.service.get_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.get("/tasks/999")

    assert response.status_code == 400
    assert "message" in response.get_json()


def test_get_task_invalid_id(client):
    response = client.get("/tasks/abc")
    assert response.status_code in (400, 404)


# =========================
# DELETE / RESTORE
# =========================

def test_delete_task_success(client):
    with patch("modules.tasks.service.soft_delete_task", return_value=None):
        response = client.patch("/tasks/1/delete")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_delete_task_not_found(client):
    with patch(
        "modules.tasks.service.soft_delete_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/999/delete")

    assert response.status_code == 400


def test_restore_task_success(client):
    with patch("modules.tasks.service.restore_task", return_value=None):
        response = client.patch("/tasks/1/restore")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_restore_task_not_found(client):
    with patch(
        "modules.tasks.service.restore_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/999/restore")

    assert response.status_code == 400


# =========================
# LIST
# =========================

def test_list_tasks(client):
    tasks = [DummyTask(task_id=1), DummyTask(task_id=2)]

    with patch("modules.tasks.service.list_tasks", return_value=tasks):
        response = client.get("/tasks")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_list_tasks_error(client):
    with patch(
        "modules.tasks.service.list_tasks",
        side_effect=ValueError("error")
    ):
        response = client.get("/tasks")

    assert response.status_code == 400


# =========================
# UPDATE
# =========================

def test_update_task_success(client):
    payload = {
        "task_title": "updated task",
        "task_due": "2099-01-02 15:45"
    }

    with patch(
        "modules.tasks.service.update_task",
        return_value=DummyTask(
            task_id=1,
            task_title="updated task",
            task_due="2099-01-02 15:45"
        )
    ):
        response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == 1
    assert data["task_title"] == "updated task"
    assert data["task_due"] == "2099-01-02 15:45"


def test_update_task_not_found(client):
    with patch(
        "modules.tasks.service.update_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/999", json={"task_title": "x"})

    assert response.status_code == 400


def test_update_task_invalid_due(client):
    payload = {"task_due": "2020-01-01 10:30"}

    with patch(
        "modules.tasks.service.update_task",
        side_effect=ValueError("Task due time cannot be in the past")
    ):
        response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 400


def test_update_task_invalid_due_format(client):
    payload = {"task_due": "2099-01-01"}

    with patch(
        "modules.tasks.service.update_task",
        side_effect=ValueError("Task due time must be in format YYYY-MM-DD HH:MM")
    ):
        response = client.patch("/tasks/1", json=payload)

    assert response.status_code == 400


def test_update_task_empty_payload(client):
    with patch(
        "modules.tasks.service.update_task",
        side_effect=ValueError("No fields to update")
    ):
        response = client.patch("/tasks/1", json={})

    assert response.status_code == 400