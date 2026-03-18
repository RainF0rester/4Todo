from __future__ import annotations

from sqlalchemy.orm import Session

from utils.jwt_utils import create_token
from .models import User
from .repo import create_user, get_user_by_username_or_email

class AuthError(Exception):
    pass

class ConflictError(Exception):
    pass

def register_user(session: Session, username: str, email: str, password: str) -> dict:
    username = username.strip()
    email = email.strip().lower()
    password = password.strip()

    if not username:
        raise ValueError("username is required")

    if not email:
        raise ValueError("email is required")

    if not password:
        raise ValueError("password is required")

    user = User(username=username, email=email, password_hash="")
    user.set_password(password)
    user = create_user(session, user)

    return user.to_json()

def login_user(session: Session, identify: str, password: str) -> dict:
    identify = identify.strip()
    password = password.strip()

    if not identify:
        raise ValueError("identify is required")
    if not password:
        raise ValueError("password is required")

    user = get_user_by_username_or_email(session, identify)
    if user is None:
        raise AuthError("invalid identify")

    if not user.check_password(password):
        raise AuthError("invalid password")

    token = create_token(user_id=user.id, username=user.username, email=user.email)

    return {
        "users": user.to_json(),
        "token": token,
    }