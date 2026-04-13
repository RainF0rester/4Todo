from flask import g
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Task
from . import repo


def _validate_task_title(title: str | None) -> str:
    title = (title or "").strip()
    if not title:
        raise ValueError("Task title is required")
    if len(title) > 100:
        raise ValueError("Task title must not exceed 100 characters")
    return title


def _parse_due_time(due: str | None) -> str | None:
    """
    Parse and validate task due time.

    - Accepts due time as string in format "YYYY-MM-DD HH:MM"
    - Returns None if due is empty
    - Raises ValueError if format is invalid or time is in the past

    This function is shared by create and update operations.
    """
    if isinstance(due, str):
        due = due.strip() or None

    if due is None:
        return None

    try:
        parsed_due = datetime.strptime(due, "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Task due time must be in format YYYY-MM-DD HH:MM")

    # do not check due time is past now or not
    # if parsed_due < datetime.now():
    #     raise ValueError("Task due time cannot be in the past")

    return str(parsed_due)


def _normalize(payload: dict) -> dict:
    title = _validate_task_title(payload.get("task_title"))
    due = _parse_due_time(payload.get("task_due"))

    desc = payload.get("task_description")
    if isinstance(desc, str):
        desc = desc.strip() or None

    level = payload.get("task_level", 0)
    if not isinstance(level, int) or not (0 <= level <= 10):
        raise ValueError("Task level must be int between 0 and 10")

    is_finished = payload.get("is_finished", 0)
    if is_finished not in (0, 1, True, False):
        raise ValueError("Task is_finished must be 0/1")
    is_finished = int(bool(is_finished))

    is_pinned = payload.get("is_pinned", 0)
    if is_pinned not in (0, 1, True, False):
        raise ValueError("Task is_pinned must be 0/1")
    is_pinned = int(bool(is_pinned))

    return {
        "task_title": title,
        "task_due": due,
        "task_description": desc,
        "task_level": level,
        "is_finished": is_finished,
        "is_pinned": is_pinned,
    }


def _normalize_update(payload: dict) -> dict:
    data = {}

    if "task_title" in payload:
        data["task_title"] = _validate_task_title(payload.get("task_title"))

    if "task_due" in payload:
        data["task_due"] = _parse_due_time(payload.get("task_due"))

    if "task_description" in payload:
        desc = payload.get("task_description")
        if isinstance(desc, str):
            desc = desc.strip() or None
        data["task_description"] = desc

    if "task_level" in payload:
        level = payload.get("task_level")
        if not isinstance(level, int) or not (0 <= level <= 10):
            raise ValueError("Task level must be int between 0 and 10")
        data["task_level"] = level

    if "is_finished" in payload:
        is_finished = payload.get("is_finished")
        if is_finished not in (0, 1, True, False):
            raise ValueError("Task is_finished must be 0/1")
        data["is_finished"] = int(bool(is_finished))

    if "is_pinned" in payload:
        is_pinned = payload.get("is_pinned")
        if is_pinned not in (0, 1, True, False):
            raise ValueError("Task is_pinned must be 0/1")
        data["is_pinned"] = int(bool(is_pinned))

    return data


def create_task(session: Session, payload: dict, user_id: int) -> Task:
    data = _normalize(payload)
    data["user_id"] = user_id
    task = Task(**data)
    return repo.create_task(session, task)

def update_task(session: Session, task_id: int, payload: dict, user_id: int) -> Task:
    task = repo.get_task(session, task_id)
    if task is None or task.is_deleted == 1:
        raise ValueError("Task not found")
    if task.user_id != user_id:
        raise ValueError("Task not found")

    data = _normalize_update(payload)
    if not data:
        raise ValueError("No fields to update")

    for key, value in data.items():
        setattr(task, key, value)

    return repo.update_task(session, task)


def get_task(session: Session, task_id: int, user_id: int) -> Task:
    task = repo.get_task(session, task_id)
    if task is None or task.is_deleted == 1:
        raise ValueError("Task not found")
    if task.user_id != user_id:
        raise ValueError("Task not found")
    return task


def soft_delete_task(session: Session, task_id: int, user_id: int) -> None:
    task = repo.get_task(session, task_id)
    if task.user_id != user_id:
        raise ValueError("Task not found")
    ok = repo.soft_delete_task(session, task_id)
    if not ok:
        raise ValueError("Task failed to delete")


def restore_task(session: Session, task_id: int, user_id: int) -> None:
    task = repo.get_task(session, task_id)
    if task.user_id != user_id:
        raise ValueError("Task not found")
    ok = repo.restore_task(session, task_id)
    if not ok:
        raise ValueError("Task failed to restore")


def list_tasks(session: Session, user_id: int, include_deleted: bool = False) -> list[Task]:
    return repo.list_tasks(session, user_id=user_id, include_deleted=include_deleted)

def list_deleted_tasks(session: Session, user_id: int) -> list[Task]:
    return repo.list_deleted_tasks(session, user_id=user_id)

def pin_task(session: Session, task_id: int, user_id: int) -> None:
    task = repo.get_task(session, task_id)
    if task.user_id != user_id:
        raise ValueError("Task not found")
    ok = repo.pin_task(session, task_id)
    if not ok:
        raise ValueError("Task failed to pin")

def unpin_task(session: Session, task_id: int, user_id: int) -> None:
    task = repo.get_task(session, task_id)
    if task.user_id != user_id:
        raise ValueError("Task not found")
    task.is_pinned = 0
    task = repo.update_task(session, task)
    if task.is_pinned != 0:
        raise ValueError("Task failed to unpin")