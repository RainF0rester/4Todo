from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Task

def create_task(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_task(session: Session, task_id: int) -> Task | None: 
    return session.get(Task, task_id)

def list_tasks(session: Session, include_deleted: bool = False) -> list[Task]:
    statement = select(Task)
    if not include_deleted:
        statement = statement.where(Task.is_deleted == 0)
    return list(session.scalars(statement).all())

def soft_delete_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task is None:
        return False

    if task.is_deleted == 1:
        return True  

    task.is_deleted = 1
    session.commit()
    return True

def restore_task(session: Session, task_id: int) -> bool:
    task = session.get(Task, task_id)
    if task is None:
        return False

    if task.is_deleted == 0:
        return True  

    task.is_deleted = 0
    session.commit()
    return True