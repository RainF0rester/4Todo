from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session
from .models import Pomodoro

def upsert_pomodoro(session: Session, user_id: int, date: str) -> Pomodoro | None:
    stmt = insert(Pomodoro).values(user_id=user_id, date=date, count=1)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "date"],
        set_={"count": Pomodoro.count + 1},
    )
    session.execute(stmt)
    session.commit()

    return session.scalar(
        select(Pomodoro).where(Pomodoro.user_id == user_id, Pomodoro.date == date)
    )

def get_by_date(session: Session, user_id: int, date: str) -> Pomodoro | None:
    stmt = select(Pomodoro).where(Pomodoro.user_id ==user_id, Pomodoro.date == date)
    return session.scalar(stmt)

def list_by_range(session: Session, user_id: int, start_date: str, end_date: str) -> list[Pomodoro]:
    stmt = select(Pomodoro)
    stmt = stmt.where(Pomodoro.user_id == user_id, Pomodoro.date >= start_date, Pomodoro.date <= end_date)
    return list(session.scalars(stmt).all())