from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from .models import User

def create_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_id(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)

def get_user_by_username(session: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return session.scalar(stmt)

def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return session.scalar(stmt)

def get_user_by_username_or_email(session: Session, identify: str) -> User | None:
    stmt = select(User).where(or_(User.username == identify, User.email == identify))
    return session.scalar(stmt)
