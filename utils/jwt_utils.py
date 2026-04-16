from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

SECRET_KEY = "LLZZ"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 4320
REFRESH_TOKEN_EXPIRE_MINUTES = 10080 # 7days

class TokenError(Exception):
    pass

class TokenRefreshError(TokenError):
    pass

def _now() -> datetime:
    return datetime.now(timezone.utc)

def create_token(user_id: int, username: str, email: str) -> str:
    """
    Create a JWT token containing user_id, username, email, iat, exp, and refresh_exp
    """
    now = _now()
    exp = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_exp = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "refresh_exp": int(refresh_exp.timestamp()),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict[str, Any]:
    """
    Decode token without verifying exp
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except jwt.InvalidTokenError as e:
        raise TokenError("Invalid token") from e


def validate_token(token: str) -> dict[str, Any]:
    """
    Validate token
    """
    payload = decode_token(token)
    required_fields = ["user_id", "username", "email", "iat", "exp", "refresh_exp"]
    for field in required_fields:
        if field not in payload:
            raise TokenError(f"Missing required field: {field}")

    now_ts = int(_now().timestamp())
    exp_ts = int(payload["exp"])
    refresh_ts = int(payload["refresh_exp"])

    if now_ts < exp_ts:
        return {
            "payload": payload,
            "state": "active",
        }

    if now_ts < refresh_ts:
        return {
            "payload": payload,
            "state": "refreshable",
        }

    raise TokenError("Refresh Window expired")

def refresh_token(old_token: str) -> str:
    """refresh token if still within refresh window"""
    result = validate_token(old_token)
    payload = result["payload"]

    return create_token(payload["user_id"], payload["username"], payload["email"])
