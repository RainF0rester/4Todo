from backend.modules.tasks.repo import (
    create_task,
    get_task,
    update_task,
    list_tasks,
    list_deleted_tasks,
    soft_delete_task,
    restore_task,
    pin_task,
)
from backend.modules.tasks.models import Task


def create_dummy_task(session, **kwargs):
    data = {
        "task_title": "test",
        "task_description": "desc",
        "task_due": "2026-01-01 10:00:00",
        "task_level": 1,
        "is_pinned": 0,
        "user_id": 1,
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
        task_due="2026-01-01 10:00:00",
        task_level=1,
        is_pinned=0,
        user_id=1,
        is_finished=0,
        is_deleted=0,
    )

    result = create_task(session, task)

    assert result.id is not None
    assert result.task_title == "new"
    assert result.user_id == 1
    assert result.is_pinned == 0
    assert result.is_deleted == 0


def test_get_task_found(session):
    task = create_dummy_task(session)

    result = get_task(session, task.id)

    assert result is not None
    assert result.id == task.id
    assert result.task_title == task.task_title


def test_get_task_not_found(session):
    result = get_task(session, 999999)

    assert result is None


def test_update_task(session):
    task = create_dummy_task(session)

    task.task_title = "updated"
    task.task_level = 5

    updated = update_task(session, task)

    assert updated.task_title == "updated"
    assert updated.task_level == 5

    db_task = session.get(Task, task.id)
    assert db_task.task_title == "updated"
    assert db_task.task_level == 5


def test_list_tasks_empty(session):
    result = list_tasks(session, user_id=1)

    assert result == []


def test_list_tasks_only_returns_current_user(session):
    mine = create_dummy_task(session, user_id=1, is_deleted=0)
    other = create_dummy_task(session, user_id=2, is_deleted=0)

    result = list_tasks(session, user_id=1, include_deleted=False)

    ids = [t.id for t in result]

    assert mine.id in ids
    assert other.id not in ids


def test_list_tasks_excludes_deleted(session):
    t1 = create_dummy_task(session, user_id=1, is_deleted=0)
    t2 = create_dummy_task(session, user_id=1, is_deleted=1)
    t3 = create_dummy_task(session, user_id=2, is_deleted=0)

    result = list_tasks(session, user_id=1, include_deleted=False)

    ids = [t.id for t in result]

    assert t1.id in ids
    assert t2.id not in ids
    assert t3.id not in ids


def test_list_tasks_include_deleted(session):
    t1 = create_dummy_task(session, user_id=1, is_deleted=0)
    t2 = create_dummy_task(session, user_id=1, is_deleted=1)
    t3 = create_dummy_task(session, user_id=2, is_deleted=1)

    result = list_tasks(session, user_id=1, include_deleted=True)

    ids = [t.id for t in result]

    assert t1.id in ids
    assert t2.id in ids
    assert t3.id not in ids


def test_list_tasks_orders_pinned_then_due_then_id(session):
    t1 = create_dummy_task(
        session,
        user_id=1,
        is_pinned=1,
        task_due="2026-01-01 08:00:00",
    )
    t2 = create_dummy_task(
        session,
        user_id=1,
        is_pinned=1,
        task_due="2026-01-01 08:00:00",
    )
    t3 = create_dummy_task(
        session,
        user_id=1,
        is_pinned=0,
        task_due="2026-01-01 07:00:00",
    )

    result = list_tasks(session, user_id=1, include_deleted=False)

    ids = [t.id for t in result]

    assert ids[0] == t1.id
    assert ids[1] == t2.id
    assert ids[0] < ids[1]
    assert ids[2] == t3.id


def test_list_deleted_tasks_empty(session):
    result = list_deleted_tasks(session, user_id=1)

    assert result == []


def test_list_deleted_tasks_is_user_scoped(session):
    mine = create_dummy_task(session, user_id=1, is_deleted=1)
    create_dummy_task(session, user_id=2, is_deleted=1)

    result = list_deleted_tasks(session, user_id=1)

    assert [t.id for t in result] == [mine.id]


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


def test_pin_task_success(session):
    task = create_dummy_task(session, is_deleted=0, is_pinned=0)

    result = pin_task(session, task.id)

    assert result is True

    updated = session.get(Task, task.id)
    assert updated.is_pinned == 1


def test_pin_task_not_found(session):
    result = pin_task(session, 999999)

    assert result is False


def test_pin_task_deleted_task(session):
    task = create_dummy_task(session, is_deleted=1, is_pinned=0)

    result = pin_task(session, task.id)

    assert result is False

    updated = session.get(Task, task.id)
    assert updated.is_pinned == 0


def test_pin_task_already_pinned(session):
    task = create_dummy_task(session, is_deleted=0, is_pinned=1)

    result = pin_task(session, task.id)

    assert result is True

    updated = session.get(Task, task.id)
    assert updated.is_pinned == 1