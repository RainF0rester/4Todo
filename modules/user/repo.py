from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from .models import User

def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_username_or_email(session: Session, identify: str) -> User | None:
    stmt = select(User).where(or_(User.email == identify, User.email == identify))
    return session.scalar(stmt)
