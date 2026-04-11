import pytest
from modules.tasks.service import create_task, update_task, get_task


def test_create_task_without_due_time(session):
    payload = {
        "task_title": "Task without due time",
        "task_description": "No deadline",
        "task_level": 1,
    }

    task = create_task(session, payload)

    assert task.id is not None
    assert task.task_title == "Task without due time"
    assert task.task_due is None