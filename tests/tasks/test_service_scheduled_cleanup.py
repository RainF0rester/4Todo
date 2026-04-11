import pytest
from modules.tasks import service

pytestmark = pytest.mark.xfail(
    reason="US6 scheduled deletion not implemented: missing scheduling metadata and cleanup process",
    strict=False,
)


def _create_task(session, title="Task A"):
    return service.create_task(
        session,
        {
            "task_title": title,
            "task_due": "2026-04-20 10:00",
            "task_description": "desc",
            "task_level": 3,
        },
    )


def test_deleted_task_should_have_scheduled_deletion_time(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    deleted_tasks = service.list_deleted_tasks(session)
    deleted = deleted_tasks[0]

    assert hasattr(deleted, "scheduled_deletion_time")
    assert deleted.scheduled_deletion_time is not None


def test_cleanup_should_remove_tasks_past_scheduled_time(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    service.cleanup_deleted_tasks(session)

    with pytest.raises(ValueError, match="Task not found"):
        service.get_task(session, task.id)


def test_cleanup_should_not_remove_tasks_before_scheduled_time(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    service.cleanup_deleted_tasks(session)

    deleted_tasks = service.list_deleted_tasks(session)
    deleted_ids = [t.id for t in deleted_tasks]

    assert task.id in deleted_ids


def test_cleanup_should_only_remove_expired_tasks(session):
    task1 = _create_task(session, "Expired Task")
    task2 = _create_task(session, "Not Expired Task")

    service.soft_delete_task(session, task1.id)
    service.soft_delete_task(session, task2.id)

    service.cleanup_deleted_tasks(session)

    deleted_tasks = service.list_deleted_tasks(session)
    deleted_ids = [t.id for t in deleted_tasks]

    assert task1.id not in deleted_ids
    assert task2.id in deleted_ids


def test_cleanup_should_not_affect_active_tasks(session):
    active_task = _create_task(session, "Active Task")

    service.cleanup_deleted_tasks(session)

    fetched = service.get_task(session, active_task.id)
    assert fetched.id == active_task.id
    assert fetched.is_deleted == 0