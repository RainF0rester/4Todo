import pytest
from modules.tasks.repo import (
    create_task,
    get_task,
    update_task,
    list_tasks,
    soft_delete_task,
    restore_task,
)
from modules.tasks.models import Task


def create_dummy_task(session, **kwargs):
    data = {
        "task_title": "test",
        "task_description": "desc",
        "task_due": "2026-01-01 10:00",
        "task_level": 1,
        "is_finished": 0,
        "is_deleted": 0,
    }

    data.update(kwargs)

    task = Task(**data)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def test_create_task(session):
    task = Task(
        task_title="new",
        task_description="desc",
        task_due="2026-01-01 10:00",
        task_level=1,
        is_finished=0,
        is_deleted=0
    )

    result = create_task(session, task)

    assert result.id is not None
    assert result.task_title == "new"


def test_get_task_found(session):
    task = create_dummy_task(session)

    result = get_task(session, task.id)

    assert result is not None
    assert result.id == task.id


def test_get_task_not_found(session):
    result = get_task(session, 999999)

    assert result is None


def test_update_task(session):
    task = create_dummy_task(session)

    task.task_title = "updated"

    updated = update_task(session, task)

    assert updated.task_title == "updated"

    db_task = session.get(Task, task.id)
    assert db_task.task_title == "updated"


def test_list_tasks_empty(session):
    result = list_tasks(session)

    assert result == []


def test_list_tasks_excludes_deleted(session):
    t1 = create_dummy_task(session, is_deleted=0)
    t2 = create_dummy_task(session, is_deleted=1)

    result = list_tasks(session, include_deleted=False)

    ids = [t.id for t in result]

    assert t1.id in ids
    assert t2.id not in ids


def test_list_tasks_include_deleted(session):
    t1 = create_dummy_task(session, is_deleted=0)
    t2 = create_dummy_task(session, is_deleted=1)

    result = list_tasks(session, include_deleted=True)

    ids = [t.id for t in result]

    assert t1.id in ids
    assert t2.id in ids


def test_soft_delete_task_success(session):
    task = create_dummy_task(session)

    result = soft_delete_task(session, task.id)

    assert result is True

    updated = session.get(Task, task.id)
    assert updated.is_deleted == 1


def test_soft_delete_task_not_found(session):
    result = soft_delete_task(session, 999999)

    assert result is False


def test_soft_delete_task_already_deleted(session):
    task = create_dummy_task(session, is_deleted=1)

    result = soft_delete_task(session, task.id)

    assert result is True

    updated = session.get(Task, task.id)
    assert updated.is_deleted == 1


def test_restore_task_success(session):
    task = create_dummy_task(session, is_deleted=1)

    result = restore_task(session, task.id)

    assert result is True

    updated = session.get(Task, task.id)
    assert updated.is_deleted == 0


def test_restore_task_not_found(session):
    result = restore_task(session, 999999)

    assert result is False


def test_restore_task_already_active(session):
    task = create_dummy_task(session, is_deleted=0)

    result = restore_task(session, task.id)

    assert result is True

    updated = session.get(Task, task.id)
    assert updated.is_deleted == 0