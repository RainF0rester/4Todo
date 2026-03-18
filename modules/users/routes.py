from apiflask import APIBlueprint, abort

from db import get_session
from .service import AuthError, ConflictError, login_user, register_user
from .schemas import LoginReqSchema, LoginRespSchema, RegisterReqSchema, RegisterRespSchema

bp = APIBlueprint('users', __name__, url_prefix='/users', tag="User")

@bp.post("/register")
@bp.input(RegisterReqSchema)
def register(json_data):
    session = get_session()
    try:
        register_user(session, username=json_data['username'], email=json_data["email"], password=json_data['password'])
        return { "status" : "ok"}
    except ConflictError as e:
        abort(400, str(e))
    except ValueError as e:
        abort(400, message=str(e))


@bp.post("/login")
@bp.input(LoginReqSchema)
@bp.output(LoginRespSchema)
def login(json_data):
    session = get_session()
    try:
        result = login_user(session, identify=json_data['identify'], password=json_data['password'])
        return result
    except AuthError as e:
        abort(401, message=str(e))
    except ValueError as e:
        abort(400, message=str(e))