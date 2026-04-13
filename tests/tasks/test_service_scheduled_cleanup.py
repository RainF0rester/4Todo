import pytest
from datetime import datetime, timedelta
from modules.tasks import service

pytestmark = pytest.mark.xfail(
    reason="Scheduled cleanup flow is not available in the current integrated task service",
    strict=False,
)


def _create_task(session, test_user, title="Task A"):
    return service.create_task(
        session,
        {
            "task_title": title,
            "task_due": "2026-04-20 10:00",
            "task_description": "desc",
            "task_level": 3,
        },
        user_id=test_user.id,
    )


def test_deleted_task_should_have_scheduled_delete_time(session, test_user):
    task = _create_task(session, test_user)

    service.soft_delete_task(session, task.id, user_id=test_user.id)

    deleted_tasks = service.list_deleted_tasks(session, user_id=test_user.id)
    deleted = deleted_tasks[0]

    assert hasattr(deleted, "scheduled_delete_time")
    assert deleted.scheduled_delete_time is not None


def test_cleanup_should_remove_tasks_past_scheduled_time(session, test_user):
    task = _create_task(session, test_user)

    service.soft_delete_task(session, task.id, user_id=test_user.id)

    deleted_tasks = service.list_deleted_tasks(session, user_id=test_user.id)
    deleted = deleted_tasks[0]
    deleted.scheduled_delete_time = datetime.now() - timedelta(minutes=1)
    session.commit()

    service.cleanup_deleted_tasks(session)

    with pytest.raises(ValueError, match="Task not found"):
        service.get_task(session, task.id, user_id=test_user.id)


def test_cleanup_should_not_remove_tasks_before_scheduled_time(session, test_user):
    task = _create_task(session, test_user)

    service.soft_delete_task(session, task.id, user_id=test_user.id)

    deleted_tasks = service.list_deleted_tasks(session, user_id=test_user.id)
    deleted = deleted_tasks[0]
    deleted.scheduled_delete_time = datetime.now() + timedelta(days=1)
    session.commit()

    service.cleanup_deleted_tasks(session)

    deleted_tasks = service.list_deleted_tasks(session, user_id=test_user.id)
    deleted_ids = [t.id for t in deleted_tasks]

    assert task.id in deleted_ids


def test_cleanup_should_only_remove_expired_tasks(session, test_user):
    task1 = _create_task(session, test_user, "Expired Task")
    task2 = _create_task(session, test_user, "Not Expired Task")

    service.soft_delete_task(session, task1.id, user_id=test_user.id)
    service.soft_delete_task(session, task2.id, user_id=test_user.id)

    deleted_tasks = service.list_deleted_tasks(session, user_id=test_user.id)
    deleted_map = {t.id: t for t in deleted_tasks}

    deleted_map[task1.id].scheduled_delete_time = datetime.now() - timedelta(minutes=1)
    deleted_map[task2.id].scheduled_delete_time = datetime.now() + timedelta(days=1)
    session.commit()

    service.cleanup_deleted_tasks(session)

    remaining_deleted_tasks = service.list_deleted_tasks(session, user_id=test_user.id)
    remaining_deleted_ids = [t.id for t in remaining_deleted_tasks]

    assert task1.id not in remaining_deleted_ids
    assert task2.id in remaining_deleted_ids


def test_cleanup_should_not_affect_active_tasks(session, test_user):
    active_task = _create_task(session, test_user, "Active Task")

    service.cleanup_deleted_tasks(session)

    fetched = service.get_task(session, active_task.id, user_id=test_user.id)
    assert fetched.id == active_task.id
    assert fetched.is_deleted == 0