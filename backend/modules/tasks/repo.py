from datetime import datetime, timedelta
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import Session
from .models import Task

SCHEDULED_DELETE_DELAY_DAYS = 7


def create_task(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_task(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def update_task(session: Session, task: Task) -> Task:
    session.commit()
    session.refresh(task)
    return task


def list_tasks(session: Session, user_id: int, include_deleted: bool = False) -> list[Task]:
    statement = select(Task)
    statement = statement.where(Task.user_id == user_id)
    if not include_deleted:
        statement = statement.where(Task.is_deleted == 0)
    statement = statement.order_by(
        desc(Task.is_pinned),
        asc(Task.task_due),
        asc(Task.id),
    )
    return list(session.scalars(statement).all())

def list_deleted_tasks(session: Session, user_id: int) -> list[Task]:
    statement = select(Task)
    statement = statement.where(Task.is_deleted == 1)
    statement = statement.where(Task.user_id == user_id)
    return list(session.scalars(statement).all())

def soft_delete_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task is None:
        return False

    if task.is_deleted == 1:
        return True

    task.is_deleted = 1
    task.scheduled_delete_time = datetime.now() + timedelta(days=SCHEDULED_DELETE_DELAY_DAYS)
    session.commit()
    session.refresh(task)
    return True


def restore_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task is None:
        return False

    if task.is_deleted == 0:
        return True

    task.is_deleted = 0
    task.scheduled_delete_time = None
    session.commit()
    session.refresh(task)
    return True


def cleanup_deleted_tasks(session: Session) -> int:
    now = datetime.now()

    statement = select(Task).where(
        Task.is_deleted == 1,
        Task.scheduled_delete_time.is_not(None),
        Task.scheduled_delete_time <= now,
    )
    tasks = list(session.scalars(statement).all())

    deleted_count = 0
    for task in tasks:
        session.delete(task)
        deleted_count += 1

    session.commit()
    return deleted_count


def pin_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task is None:
        return False
    if task.is_deleted == 1:
        return False
    task.is_pinned = 1
    session.commit()
    return True