"""
Authentication decorator for global authorization control.

This module provides decorators to protect routes and require valid JWT tokens.
"""

from functools import wraps
from flask import request
from apiflask import abort

from .jwt_utils import validate_token, TokenError


def require_auth(f):
    """
    Decorator to require valid JWT token for route access.
    
    The token should be provided in the Authorization header:
    Authorization: Bearer <token>
    
    If valid, the user_id and payload are injected into the route function.
    
    Example:
        @bp.get("/profile")
        @require_auth
        def get_profile(user_id, payload):
            # user_id contains the authenticated user's ID
            # payload contains the full token payload
            return {"user_id": user_id}
    
    Returns:
        401 Unauthorized if token is missing or invalid
        403 Forbidden if token is expired (but can be refreshed)
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            abort(401, message="Missing authorization token")
        
        # Expect format: "Bearer <token>"
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                abort(401, message="Invalid authorization scheme, expected 'Bearer'")
        except ValueError:
            abort(401, message="Invalid authorization header format")
        
        # Validate token
        try:
            result = validate_token(token)
            payload = result['payload']
            state = result['state']
            
            # If token is expired but refreshable, return 403 with refresh hint
            if state == 'refreshable':
                abort(403, message="Token expired, please refresh your token")
            
            # Token is active, inject user_id and payload into function
            user_id = payload.get('user_id')
            kwargs['user_id'] = user_id
            kwargs['payload'] = payload
            
            return f(*args, **kwargs)
            
        except TokenError as e:
            abort(401, message=str(e))
    
    return wrapper


def require_auth_optional(f):
    """
    Decorator for optional authentication.
    
    If a valid token is provided, inject user_id and payload.
    If no token or invalid token, proceed without authentication.
    
    Example:
        @bp.get("/posts")
        @require_auth_optional
        def get_posts(user_id=None, payload=None):
            if user_id:
                # Authenticated request
                return {"posts": "user's posts"}
            else:
                # Anonymous request
                return {"posts": "public posts"}
    
    Returns:
        user_id=None and payload=None if no token provided
        user_id and payload injected if valid token provided
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        # If no auth header, call function without auth info
        if not auth_header:
            kwargs['user_id'] = None
            kwargs['payload'] = None
            return f(*args, **kwargs)
        
        # Try to validate token if provided
        try:
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                # Invalid scheme, treat as anonymous
                kwargs['user_id'] = None
                kwargs['payload'] = None
                return f(*args, **kwargs)
        except ValueError:
            # Invalid format, treat as anonymous
            kwargs['user_id'] = None
            kwargs['payload'] = None
            return f(*args, **kwargs)
        
        # Validate token
        try:
            result = validate_token(token)
            payload = result['payload']
            state = result['state']
            
            # For optional auth, we allow both active and refreshable tokens
            # but still pass the state if needed
            if state == 'refreshable':
                # Token is expired, but still inject for reference
                # The client should refresh before the refresh window expires
                pass
            
            user_id = payload.get('user_id')
            kwargs['user_id'] = user_id
            kwargs['payload'] = payload
            
            return f(*args, **kwargs)
            
        except TokenError:
            # If token validation fails, treat as anonymous
            kwargs['user_id'] = None
            kwargs['payload'] = None
            return f(*args, **kwargs)
    
    return wrapper


def require_auth_with_scope(*required_scopes):
    """
    Decorator to require token with specific scopes.
    
    This is a more advanced decorator that can validate scopes if your
    token payload includes a 'scopes' field.
    
    Example:
        @bp.post("/admin/users")
        @require_auth_with_scope('admin', 'user:create')
        def create_admin_user(user_id, payload):
            # Only accessible if token has 'admin' or 'user:create' scope
            return {"status": "created"}
    
    Args:
        *required_scopes: One or more required scopes. User must have at least one.
    
    Returns:
        401 Unauthorized if token is missing or invalid
        403 Forbidden if token is valid but lacks required scopes
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extract and validate token (same as require_auth)
            auth_header = request.headers.get('Authorization', '')
            
            if not auth_header:
                abort(401, message="Missing authorization token")
            
            try:
                scheme, token = auth_header.split(' ', 1)
                if scheme.lower() != 'bearer':
                    abort(401, message="Invalid authorization scheme, expected 'Bearer'")
            except ValueError:
                abort(401, message="Invalid authorization header format")
            
            try:
                result = validate_token(token)
                payload = result['payload']
                state = result['state']
                
                if state == 'refreshable':
                    abort(403, message="Token expired, please refresh your token")
                
                # Check scopes
                token_scopes = payload.get('scopes', [])
                if isinstance(token_scopes, str):
                    token_scopes = [token_scopes]
                
                # Check if user has at least one required scope
                has_required_scope = any(scope in token_scopes for scope in required_scopes)
                
                if not has_required_scope:
                    abort(403, message=f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}")
                
                user_id = payload.get('user_id')
                kwargs['user_id'] = user_id
                kwargs['payload'] = payload
                
                return f(*args, **kwargs)
                
            except TokenError as e:
                abort(401, message=str(e))
        
        return wrapper
    return decorator

