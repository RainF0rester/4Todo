from modules.tasks import service


def _create_task(session, title="Task A", due="2026-04-20 10:00", level=3):
    return service.create_task(
        session,
        {
            "task_title": title,
            "task_due": due,
            "task_description": "desc",
            "task_level": level,
        },
    )


def test_soft_delete_marks_task_as_deleted(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    deleted = service.list_deleted_tasks(session)
    assert len(deleted) == 1
    assert deleted[0].id == task.id
    assert deleted[0].is_deleted == 1


def test_soft_deleted_task_is_hidden_from_list_tasks(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    tasks = service.list_tasks(session)
    task_ids = [t.id for t in tasks]

    assert task.id not in task_ids


def test_soft_deleted_task_cannot_be_retrieved(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    try:
        service.get_task(session, task.id)
        assert False, "Expected ValueError for deleted task"
    except ValueError as e:
        assert str(e) == "Task not found"


def test_soft_deleted_task_remains_in_deleted_list(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)

    deleted_tasks = service.list_deleted_tasks(session)
    deleted_ids = [t.id for t in deleted_tasks]

    assert task.id in deleted_ids


def test_restore_task_makes_deleted_task_visible_again(session):
    task = _create_task(session)

    service.soft_delete_task(session, task.id)
    service.restore_task(session, task.id)

    restored = service.get_task(session, task.id)
    assert restored.id == task.id
    assert restored.is_deleted == 0

    visible_tasks = service.list_tasks(session)
    visible_ids = [t.id for t in visible_tasks]
    assert task.id in visible_ids


def test_soft_delete_nonexistent_task_raises_value_error(session):
    try:
        service.soft_delete_task(session, 9999)
        assert False, "Expected ValueError for nonexistent task"
    except ValueError as e:
        assert str(e) == "Task not found"


def test_restore_nonexistent_task_raises_value_error(session):
    try:
        service.restore_task(session, 9999)
        assert False, "Expected ValueError for nonexistent task"
    except ValueError as e:
        assert str(e) == "Task not found"


def test_active_tasks_are_not_affected_when_other_task_is_deleted(session):
    task1 = _create_task(session, title="Task 1")
    task2 = _create_task(session, title="Task 2")

    service.soft_delete_task(session, task1.id)

    remaining_tasks = service.list_tasks(session)
    remaining_ids = [t.id for t in remaining_tasks]

    assert task1.id not in remaining_ids
    assert task2.id in remaining_ids

    task2_fetched = service.get_task(session, task2.id)
    assert task2_fetched.task_title == "Task 2"
    assert task2_fetched.is_deleted == 0