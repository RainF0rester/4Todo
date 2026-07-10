from datetime import date

from sqlalchemy.orm import Session

from .models import Pomodoro
from . import repo

def log_pomodoro(session: Session, user_id: int) -> Pomodoro | None:
    today = date.today().isoformat()
    return repo.upsert_pomodoro(session, user_id, today)

def get_today(session: Session, user_id: int) -> Pomodoro | None:
    today = date.today().isoformat()
    return repo.get_by_date(session, user_id, today)

def get_range(session: Session, user_id: int, start_date, end_date) -> list[Pomodoro]:
    _valid_date(start_date)
    _valid_date(end_date)
    if start_date > end_date:
        raise ValueError(f"start_date must be before end_date")
    return repo.list_by_range(session, user_id, start_date, end_date)

def _valid_date(d: str) -> None:
    try:
        date.fromisoformat(d)
    except ValueError:
        raise ValueError(f"Invalid date format: {d}, expected YYYY-MM-DD")