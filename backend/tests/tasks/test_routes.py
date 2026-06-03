from unittest.mock import ANY, patch


class DummyTask:
    def __init__(
        self,
        task_id=1,
        task_title="test task",
        task_due="2099-01-01 10:30",
        task_description=None,
        task_level=1,
        is_finished=0,
        is_pinned=0,
        user_id=123,
    ):
        self.task_id = task_id
        self.task_title = task_title
        self.task_due = task_due
        self.task_description = task_description
        self.task_level = task_level
        self.is_finished = is_finished
        self.is_pinned = is_pinned
        self.user_id = user_id

    def to_dict(self):
        return {
            "id": self.task_id,
            "task_title": self.task_title,
            "task_due": self.task_due,
            "task_description": self.task_description,
            "task_level": self.task_level,
            "is_finished": self.is_finished,
            "is_pinned": self.is_pinned,
            "user_id": self.user_id,
        }


def valid_payload():
    return {
        "task_title": "test task",
        "task_due": "2099-01-01 10:30",
        "task_description": "test desc",
        "task_level": 1,
        "is_pinned": 0,
    }


def auth_headers():
    return {'Authorization': 'Bearer valid_token'}


def _auth_patch():
    return patch(
        "backend.utils.auth_decorator.validate_token",
        return_value={"state": "active", "payload": {"user_id": 123}},
    )


# =========================
# CREATE
# =========================

def test_create_task_success(client):
    with _auth_patch(), patch("backend.modules.tasks.service.create_task", return_value=DummyTask()) as mock_create:
        response = client.post("/tasks", json=valid_payload(), headers=auth_headers())

    assert response.status_code == 201
    data = response.get_json()
    assert data["task_title"] == "test task"
    assert data["is_pinned"] == 0
    mock_create.assert_called_once_with(
        ANY,
        valid_payload(),
        user_id=123,
    )


def test_create_task_validation_error(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.create_task",
        side_effect=ValueError("invalid task")
    ):
        response = client.post("/tasks", json=valid_payload(), headers=auth_headers())

    assert response.status_code == 400
    assert "message" in response.get_json()


def test_create_task_invalid_due_format(client):
    payload = valid_payload()
    payload["task_due"] = "2099-01-01"

    with _auth_patch(), patch(
        "backend.modules.tasks.service.create_task",
        side_effect=ValueError("Task due time must be in format YYYY-MM-DD HH:MM")
    ):
        response = client.post("/tasks", json=payload, headers=auth_headers())

    assert response.status_code == 400


def test_create_task_past_due_time(client):
    payload = valid_payload()
    payload["task_due"] = "2020-01-01 10:30"

    with _auth_patch(), patch(
        "backend.modules.tasks.service.create_task",
        side_effect=ValueError("Task due time cannot be in the past")
    ):
        response = client.post("/tasks", json=payload, headers=auth_headers())

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
    with _auth_patch(), patch(
        "backend.modules.tasks.service.get_task",
        return_value=DummyTask(task_id=1)
    ) as mock_get:
        response = client.get("/tasks/1", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()["id"] == 1
    mock_get.assert_called_once_with(ANY, 1, user_id=123)


def test_get_task_not_found(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.get_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.get("/tasks/999", headers=auth_headers())

    assert response.status_code == 400
    assert "message" in response.get_json()


def test_get_task_invalid_id(client):
    with _auth_patch():
        response = client.get("/tasks/abc", headers=auth_headers())
    assert response.status_code in (400, 404)


# =========================
# DELETE / RESTORE
# =========================

def test_delete_task_success(client):
    with _auth_patch(), patch("backend.modules.tasks.service.soft_delete_task", return_value=None) as mock_delete:
        response = client.patch("/tasks/1/delete", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    mock_delete.assert_called_once_with(ANY, 1, user_id=123)


def test_delete_task_not_found(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.soft_delete_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/999/delete", headers=auth_headers())

    assert response.status_code == 400


def test_restore_task_success(client):
    with _auth_patch(), patch("backend.modules.tasks.service.restore_task", return_value=None) as mock_restore:
        response = client.patch("/tasks/1/restore", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    mock_restore.assert_called_once_with(ANY, 1, user_id=123)


def test_restore_task_not_found(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.restore_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/999/restore", headers=auth_headers())

    assert response.status_code == 400


# =========================
# LIST
# =========================

def test_list_tasks(client):
    tasks = [DummyTask(task_id=1), DummyTask(task_id=2)]

    with _auth_patch(), patch("backend.modules.tasks.service.list_tasks", return_value=tasks) as mock_list:
        response = client.get("/tasks", headers=auth_headers())

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["is_pinned"] == 0
    mock_list.assert_called_once_with(ANY, include_deleted=False, user_id=123)


def test_list_tasks_error(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.list_tasks",
        side_effect=ValueError("error")
    ):
        response = client.get("/tasks", headers=auth_headers())

    assert response.status_code == 400


def test_list_deleted_tasks_success(client):
    tasks = [DummyTask(task_id=1, is_pinned=1), DummyTask(task_id=2, is_pinned=0)]

    with _auth_patch(), patch("backend.modules.tasks.service.list_deleted_tasks", return_value=tasks) as mock_list:
        response = client.get("/tasks/deleted", headers=auth_headers())

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    mock_list.assert_called_once_with(ANY, user_id=123)


def test_list_deleted_tasks_error(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.list_deleted_tasks",
        side_effect=ValueError("error")
    ):
        response = client.get("/tasks/deleted", headers=auth_headers())

    assert response.status_code == 400


# =========================
# UPDATE
# =========================

def test_update_task_success(client):
    payload = {
        "task_title": "updated task",
        "task_due": "2099-01-02 15:45"
    }

    with _auth_patch(), patch(
        "backend.modules.tasks.service.update_task",
        return_value=DummyTask(
            task_id=1,
            task_title="updated task",
            task_due="2099-01-02 15:45"
        )
    ) as mock_update:
        response = client.patch("/tasks/1", json=payload, headers=auth_headers())

    assert response.status_code == 200

    data = response.get_json()
    assert data["id"] == 1
    assert data["task_title"] == "updated task"
    assert data["task_due"] == "2099-01-02 15:45"
    mock_update.assert_called_once_with(ANY, 1, payload, user_id=123)


def test_update_task_not_found(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.update_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/999", json={"task_title": "x"}, headers=auth_headers())

    assert response.status_code == 400


def test_update_task_invalid_due(client):
    payload = {"task_due": "2020-01-01 10:30"}

    with _auth_patch(), patch(
        "backend.modules.tasks.service.update_task",
        side_effect=ValueError("Task due time cannot be in the past")
    ):
        response = client.patch("/tasks/1", json=payload, headers=auth_headers())

    assert response.status_code == 400


def test_update_task_invalid_due_format(client):
    payload = {"task_due": "2099-01-01"}

    with _auth_patch(), patch(
        "backend.modules.tasks.service.update_task",
        side_effect=ValueError("Task due time must be in format YYYY-MM-DD HH:MM")
    ):
        response = client.patch("/tasks/1", json=payload, headers=auth_headers())

    assert response.status_code == 400


def test_update_task_empty_payload(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.update_task",
        side_effect=ValueError("No fields to update")
    ):
        response = client.patch("/tasks/1", json={}, headers=auth_headers())

    assert response.status_code == 400


# =========================
# PIN / UNPIN
# =========================

def test_pin_task_success(client):
    with _auth_patch(), patch("backend.modules.tasks.service.pin_task", return_value=None) as mock_pin:
        response = client.patch("/tasks/1/pin", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    mock_pin.assert_called_once_with(ANY, 1, user_id=123)


def test_pin_task_not_found(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.pin_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/1/pin", headers=auth_headers())

    assert response.status_code == 400


def test_unpin_task_success(client):
    with _auth_patch(), patch("backend.modules.tasks.service.unpin_task", return_value=None) as mock_unpin:
        response = client.patch("/tasks/1/unpin", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    mock_unpin.assert_called_once_with(ANY, 1, user_id=123)


def test_unpin_task_not_found(client):
    with _auth_patch(), patch(
        "backend.modules.tasks.service.unpin_task",
        side_effect=ValueError("Task not found")
    ):
        response = client.patch("/tasks/1/unpin", headers=auth_headers())

    assert response.status_code == 400
