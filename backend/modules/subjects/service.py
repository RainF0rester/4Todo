from datetime import datetime
from sqlalchemy.orm import Session
from .models import Subject
from . import repo
import uuid

def _validate_name(name: str | None) -> str:
    name = (name or "").strip()
    if not name:
        raise ValueError("Subject name is required")
    if len(name) > 100:
        raise ValueError("Subject name must not exceed 100 characters")
    return name

def _validate_time_range(start_time: datetime | None, finish_time: datetime | None) -> None:
    if start_time == None or finish_time == None:
                return
    try:
        is_valid_range = start_time <= finish_time
    except TypeError:
        raise ValueError("Invalid time range: start_time and finish_time must be datetime objects or None")
    if not is_valid_range:
        raise ValueError("Invalid time range: start_time must be less than or equal to finish_time")  


def get_subject_for_user(session: Session, subject_id: uuid.UUID, user_id: int) -> Subject:
    """
    Get a subject by ID for a specific user.
    Returns the subject if it exists and belongs to the user, otherwise returns ValueError.
    """
    subject = repo.get_subject(session, subject_id)
    if subject is None or subject.user_id != user_id:
        raise ValueError("Subject not found")
    return subject

def create_subject(session: Session, data: dict, user_id: int) -> Subject:
    """
    Create a new subject for a specific user.
    Returns the created subject.
    """
   
    data["name"] = _validate_name(data.get("name"))
    _validate_time_range(data.get("start_time"), data.get("finish_time"))
    data["user_id"] = user_id
    subject = Subject(**data)
    return repo.create_subject(session, subject)

def list_subjects(session: Session, user_id: int) -> list[Subject]:
    """
    List all subjects for a specific user.
    Returns a list of subjects.
    """
    return repo.list_subjects(session, user_id)

def update_subject(session: Session, subject_id: uuid.UUID, data: dict, user_id: int) -> Subject:
    """
    Update an existing subject for a specific user.
    Returns the updated subject.
    Raises ValueError if the subject does not exist or does not belong to the user.
    """
    
    subject = get_subject_for_user(session, subject_id, user_id)
    if "name" in data:
        data["name"] = _validate_name(data.get("name"))
    start = data.get("start_time", subject.start_time)
    finish = data.get("finish_time", subject.finish_time)
    _validate_time_range(start, finish)

    for key, value in data.items():
        setattr(subject, key, value)

    return repo.update_subject(session, subject)

def delete_subject(session: Session, subject_id: uuid.UUID, user_id: int) -> None:
    """
    Delete an existing subject for a specific user.
    Raises ValueError if the subject does not exist or does not belong to the user.
    """
    subject = get_subject_for_user(session, subject_id, user_id)

    repo.delete_subject(session, subject)