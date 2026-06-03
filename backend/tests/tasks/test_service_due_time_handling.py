from backend.modules.tasks.service import create_task, update_task, get_task


def test_create_task_without_due_time(session, test_user):
    payload = {
        "task_title": "Task without due time",
        "task_description": "No deadline",
        "task_level": 1,
    }

    task = create_task(session, payload, user_id=test_user.id)

    assert task.id is not None
    assert task.task_title == "Task without due time"
    assert task.task_description == "No deadline"
    assert task.task_level == 1
    assert task.task_due is None
    assert task.is_finished == 0
    assert task.is_pinned == 0


def test_create_task_with_due_time(session, test_user):
    payload = {
        "task_title": "Task with due time",
        "task_description": "Has deadline",
        "task_due": "2026-04-20 12:00",
        "task_level": 2,
    }

    task = create_task(session, payload, user_id=test_user.id)

    assert task.id is not None
    assert task.task_title == "Task with due time"
    assert task.task_description == "Has deadline"
    assert task.task_level == 2
    assert task.task_due == "2026-04-20 12:00:00"
    assert task.is_finished == 0
    assert task.is_pinned == 0


def test_create_task_with_blank_due_time_becomes_none(session, test_user):
    payload = {
        "task_title": "Blank due time task",
        "task_description": "Blank due time should become None",
        "task_due": "   ",
        "task_level": 2,
    }

    task = create_task(session, payload, user_id=test_user.id)

    assert task.id is not None
    assert task.task_title == "Blank due time task"
    assert task.task_due is None


def test_update_task_remove_due_time_with_none(session, test_user):
    created = create_task(
        session,
        {
            "task_title": "Task to clear due time",
            "task_due": "2026-04-20 12:00",
            "task_description": "Before update",
            "task_level": 3,
        },
        user_id=test_user.id,
    )

    updated = update_task(
        session,
        created.id,
        {
            "task_due": None
        },
        user_id=test_user.id,
    )

    assert updated.id == created.id
    assert updated.task_title == "Task to clear due time"
    assert updated.task_description == "Before update"
    assert updated.task_level == 3
    assert updated.task_due is None


def test_update_task_remove_due_time_with_empty_string(session, test_user):
    created = create_task(
        session,
        {
            "task_title": "Task to clear due time by empty string",
            "task_due": "2026-04-20 12:00",
            "task_description": "Before update",
            "task_level": 3,
        },
        user_id=test_user.id,
    )

    updated = update_task(
        session,
        created.id,
        {
            "task_due": ""
        },
        user_id=test_user.id,
    )

    assert updated.id == created.id
    assert updated.task_due is None


def test_task_without_due_time_can_still_be_retrieved(session, test_user):
    created = create_task(
        session,
        {
            "task_title": "Task without due time",
            "task_description": "Still functional",
            "task_level": 4,
        },
        user_id=test_user.id,
    )

    task = get_task(session, created.id, user_id=test_user.id)

    assert task.id == created.id
    assert task.task_title == "Task without due time"
    assert task.task_description == "Still functional"
    assert task.task_level == 4
    assert task.task_due is None


def test_task_without_due_time_can_still_be_updated(session, test_user):
    created = create_task(
        session,
        {
            "task_title": "Original title",
            "task_description": "Original description",
            "task_level": 1,
        },
        user_id=test_user.id,
    )

    updated = update_task(
        session,
        created.id,
        {
            "task_title": "Updated title",
            "task_description": "Updated description",
            "task_level": 5,
        },
        user_id=test_user.id,
    )

    assert updated.id == created.id
    assert updated.task_title == "Updated title"
    assert updated.task_description == "Updated description"
    assert updated.task_level == 5
    assert updated.task_due is None


def test_update_task_without_due_time_to_add_due_time(session, test_user):
    created = create_task(
        session,
        {
            "task_title": "Task without due time",
            "task_description": "Before adding due time",
            "task_level": 2,
        },
        user_id=test_user.id,
    )

    updated = update_task(
        session,
        created.id,
        {
            "task_due": "2026-04-21 09:30"
        },
        user_id=test_user.id,
    )

    assert updated.id == created.id
    assert updated.task_due == "2026-04-21 09:30:00"


def test_update_task_keeps_other_fields_unchanged_when_removing_due_time(session, test_user):
    created = create_task(
        session,
        {
            "task_title": "Keep fields unchanged",
            "task_due": "2026-04-20 12:00",
            "task_description": "Description stays",
            "task_level": 6,
            "is_finished": 1,
        },
        user_id=test_user.id,
    )

    updated = update_task(
        session,
        created.id,
        {
            "task_due": None
        },
        user_id=test_user.id,
    )

    assert updated.task_title == "Keep fields unchanged"
    assert updated.task_description == "Description stays"
    assert updated.task_level == 6
    assert updated.is_finished == 1
    assert updated.task_due is None