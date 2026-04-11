from __future__ import annotations

from sqlalchemy.orm import Session

from utils.jwt_utils import create_token, refresh_token
from .models import User
from .repo import create_user, get_user_by_username_or_email, get_user_by_email, get_user_by_username

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
    # TODO: username valid check

    if not email:
        raise ValueError("email is required")
    # TODO: email valid check

    if not password:
        raise ValueError("password is required")
    # TODO: password valid check

    if get_user_by_email(session, email):
        raise ConflictError("email has already been registered")

    if get_user_by_username(session, username):
        raise ConflictError("username has already been registered")

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
        "user": user.to_json(),
        "token": token,
    }

def token_refresh(token: str) -> dict:
    old_token = token.split("Bearer ")[1]
    new_token = refresh_token(old_token)
    return {
        "token": new_token,
    }