from functools import wraps
from flask import request, g
from apiflask import abort

from .jwt_utils import validate_token, TokenError

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            abort(401, message="Missing authorization token")

        # jwt token
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                abort(401, message="Invalid authorization")
        except ValueError:
            abort(401, message="Invalid authorization")

        # Validate token
        try:
            result = validate_token(token)
            payload = result['payload']
            state = result['state']

            # If token is expired but refreshable, return 403 with refresh hint
            if state == 'refreshable':
                abort(401, message="Token expired, please refresh your token")

            # Token is active, inject user_id and payload into function
            user_id = payload.get('user_id')
            g.user_id = user_id

            return f(*args, **kwargs)

        except TokenError as e:
            abort(401, message=str(e))

    return wrapper

