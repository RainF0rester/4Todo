from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Subject
import uuid

def create_subject(session: Session, subject: Subject) -> Subject:
    session.add(subject)
    session.commit()
    session.refresh(subject)
    return subject

def get_subject(session: Session, subject_id: uuid.UUID) -> Subject | None:
    return session.get(Subject, subject_id)

def list_subjects(session: Session, user_id: int) -> list[Subject]:
    statement = select(Subject)
    statement = statement.where(Subject.user_id == user_id)
    return list(session.scalars(statement).all())

def update_subject(session: Session, subject: Subject) -> Subject:
    session.commit()
    session.refresh(subject)
    return subject

def delete_subject(session: Session, subject: Subject) -> None:
    session.delete(subject)
    session.commit()