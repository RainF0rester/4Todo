from datetime import datetime
from sqlalchemy.orm import Session
from .models import Task
from . import repo

def _normalize(payload: dict) -> dict:
    title = (payload.get("task_title") or "").strip()
    if not title:
        raise ValueError("Task title is required")

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

    return {
        "task_title": title,
        "task_due": due,
        "task_description": desc,
        "task_level": level,
        "is_finished": is_finished,
    }

def create_task(session: Session, payload: dict) -> Task:
    data = _normalize(payload)
    task = Task(**data)
    return repo.create_task(session, task)

def get_task(session: Session, task_id: int) -> Task:
    task = repo.get_task(session, task_id)
    if task is None or task.is_deleted == 1:
        raise ValueError("Task not found")
    return task

def soft_delete_task(session: Session, task_id: int) -> None:
    """
    Soft delete a task by setting is_deleted to 1.
    Raises ValueError if task does not exist.
    """
    ok = repo.soft_delete_task(session, task_id)
    if not ok:
        raise ValueError("Task not found")

def restore_task(session: Session, task_id: int) -> None:
    """
    Restore a previously soft-deleted task.
    Raises ValueError if task does not exist.
    """
    ok = repo.restore_task(session, task_id)
    if not ok:
        raise ValueError("Task not found")
    
def list_tasks(session: Session, include_deleted: bool = False) -> list[Task]:
    """
    Return all tasks.
    By default excludes soft-deleted tasks.
    """
    return repo.list_tasks(session, include_deleted=include_deleted)

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

    parsed_due = datetime.strptime(due, "%Y-%m-%d %H:%M")

    if parsed_due < datetime.now():
        raise ValueError("Task due time cannot be in the past")

    return due