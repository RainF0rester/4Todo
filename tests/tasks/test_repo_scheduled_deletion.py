from modules.tasks.models import Task
from modules.tasks import repo


def _make_task(title="Task A", due="2026-04-20 10:00", level=3):
    return Task(
        task_title=title,
        task_due=due,
        task_description="desc",
        task_level=level,
        is_finished=0,
        is_deleted=0,
    )


def test_soft_delete_task_sets_is_deleted_to_1(session):
    task = repo.create_task(session, _make_task())

    ok = repo.soft_delete_task(session, task.id)

    assert ok is True

    fetched = repo.get_task(session, task.id)
    assert fetched is not None
    assert fetched.is_deleted == 1


def test_soft_delete_nonexistent_task_returns_false(session):
    ok = repo.soft_delete_task(session, 9999)
    assert ok is False


def test_list_tasks_excludes_deleted_tasks_by_default(session):
    active = repo.create_task(session, _make_task(title="Active"))
    deleted = repo.create_task(session, _make_task(title="Deleted"))

    repo.soft_delete_task(session, deleted.id)

    tasks = repo.list_tasks(session)
    ids = [t.id for t in tasks]

    assert active.id in ids
    assert deleted.id not in ids


def test_list_tasks_can_include_deleted_tasks(session):
    active = repo.create_task(session, _make_task(title="Active"))
    deleted = repo.create_task(session, _make_task(title="Deleted"))

    repo.soft_delete_task(session, deleted.id)

    tasks = repo.list_tasks(session, include_deleted=True)
    ids = [t.id for t in tasks]

    assert active.id in ids
    assert deleted.id in ids


def test_list_deleted_tasks_returns_only_deleted_tasks(session):
    active = repo.create_task(session, _make_task(title="Active"))
    deleted = repo.create_task(session, _make_task(title="Deleted"))

    repo.soft_delete_task(session, deleted.id)

    tasks = repo.list_deleted_tasks(session)
    ids = [t.id for t in tasks]

    assert deleted.id in ids
    assert active.id not in ids


def test_restore_task_sets_is_deleted_to_0(session):
    task = repo.create_task(session, _make_task())

    repo.soft_delete_task(session, task.id)
    ok = repo.restore_task(session, task.id)

    assert ok is True

    fetched = repo.get_task(session, task.id)
    assert fetched is not None
    assert fetched.is_deleted == 0