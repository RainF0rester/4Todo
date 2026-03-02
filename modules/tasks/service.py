from datetime import datetime
from sqlalchemy.orm import Session
from .models import Task
from . import repo

def _normalize(payload: dict) -> dict:
    title = (payload.get("task_title") or "").strip()
    if not title:
        raise ValueError("Task title is required")

    due = payload.get("task_due")
    if isinstance(due, str):
        due = due.strip() or None
    if due is not None:
        datetime.strptime(due, "%Y-%m-%d")
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

def get_task(session: Session, task_id: str) -> Task:
    task = repo.get_task(session, task_id)
    if task is None:
        raise KeyError("not found")
    return task