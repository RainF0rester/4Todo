from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Task

def create_task(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

def get_task(session: Session, task_id: str) -> Task | None:
    return session.get(Task, task_id)