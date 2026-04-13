import pytest
from modules.tasks.models import Task


def _create_task_directly(session, user_id, title="Task A", due="2026-04-20 10:00:00", level=3):
    task = Task(
        task_title=title,
        task_due=due,
        task_description="desc",
        task_level=level,
        is_finished=0,
        is_deleted=0,
        is_pinned=0,
        user_id=user_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def test_delete_task_route_returns_ok(client, session, monkeypatch, test_user, auth_headers):
    from modules.tasks import routes

    monkeypatch.setattr(routes, "get_session", lambda: session)

    task = _create_task_directly(session, user_id=test_user.id)

    response = client.patch(f"/tasks/{task.id}/delete", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_deleted_task_is_not_returned_by_get_route(client, session, monkeypatch, test_user, auth_headers):
    from modules.tasks import routes

    monkeypatch.setattr(routes, "get_session", lambda: session)

    task = _create_task_directly(session, user_id=test_user.id)

    delete_response = client.patch(f"/tasks/{task.id}/delete", headers=auth_headers)
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task.id}", headers=auth_headers)
    assert get_response.status_code == 400

    data = get_response.get_json()
    assert "Task not found" in data["message"]


def test_deleted_task_is_hidden_from_list_route(client, session, monkeypatch, test_user, auth_headers):
    from modules.tasks import routes

    monkeypatch.setattr(routes, "get_session", lambda: session)

    visible_task = _create_task_directly(session, user_id=test_user.id, title="Visible Task")
    deleted_task = _create_task_directly(session, user_id=test_user.id, title="Deleted Task")

    response = client.patch(f"/tasks/{deleted_task.id}/delete", headers=auth_headers)
    assert response.status_code == 200

    list_response = client.get("/tasks", headers=auth_headers)
    assert list_response.status_code == 200

    data = list_response.get_json()
    titles = [item["task_title"] for item in data]

    assert "Visible Task" in titles
    assert "Deleted Task" not in titles
    assert len(data) == 1
    assert data[0]["id"] == visible_task.id


def test_deleted_task_appears_in_deleted_list_route(client, session, monkeypatch, test_user, auth_headers):
    from modules.tasks import routes

    monkeypatch.setattr(routes, "get_session", lambda: session)

    task = _create_task_directly(session, user_id=test_user.id, title="Deleted Task")

    response = client.patch(f"/tasks/{task.id}/delete", headers=auth_headers)
    assert response.status_code == 200

    deleted_response = client.get("/tasks/deleted", headers=auth_headers)
    assert deleted_response.status_code == 200

    data = deleted_response.get_json()
    ids = [item["id"] for item in data]

    assert task.id in ids


def test_restore_task_route_makes_task_visible_again(client, session, monkeypatch, test_user, auth_headers):
    from modules.tasks import routes

    monkeypatch.setattr(routes, "get_session", lambda: session)

    task = _create_task_directly(session, user_id=test_user.id, title="Recover Me")

    delete_response = client.patch(f"/tasks/{task.id}/delete", headers=auth_headers)
    assert delete_response.status_code == 200

    restore_response = client.patch(f"/tasks/{task.id}/restore", headers=auth_headers)
    assert restore_response.status_code == 200

    get_response = client.get(f"/tasks/{task.id}", headers=auth_headers)
    assert get_response.status_code == 200

    data = get_response.get_json()
    assert data["id"] == task.id
    assert data["task_title"] == "Recover Me"


# @pytest.mark.xfail(reason="Current service.soft_delete_task does not safely handle nonexistent task before user_id check")
def test_delete_nonexistent_task_route_returns_400(client, session, monkeypatch, auth_headers):
    from modules.tasks import routes

    monkeypatch.setattr(routes, "get_session", lambda: session)

    response = client.patch("/tasks/9999/delete", headers=auth_headers)
    assert response.status_code == 400

    data = response.get_json()
    assert "Task not found" in data["message"]