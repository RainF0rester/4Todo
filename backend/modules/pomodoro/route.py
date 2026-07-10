from apiflask import APIBlueprint, abort
from flask import g
from sqlalchemy.sql.functions import count

from . import service
from backend.db import get_session
from backend.modules.pomodoro.schmas import PomodoroSchema, PomodoroRangeQuerySchema
from backend.utils.auth_decorator import require_auth

bp = APIBlueprint('pomodoro', __name__, url_prefix='/pomodoro', tag="pomodoro")

@bp.post("")
@bp.output(PomodoroSchema, status_code=201)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def log_pomodoro():
    session = get_session()
    try:
        user_id = int(g.user_id)
        return service.log_pomodoro(session, user_id).to_json()
    except ValueError as e:
        abort(400, message=str(e))

@bp.get("/today")
@bp.output(PomodoroSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_today():
    session = get_session()
    try:
        user_id = int(g.user_id)
        records = service.get_today(session, user_id)
        if records is None:
            return {"id": None, "user_id": user_id, "date": None, "count": 0}
        return records.to_json()
    except ValueError as e:
        abort(400, message=str(e))

@bp.get("/range")
@bp.input(PomodoroRangeQuerySchema, arg_name="query", location="query")
@bp.output(PomodoroSchema(many=True))
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_range(query):
    session = get_session()
    try:
        user_id = int(g.user_id)
        records = service.get_range(session, user_id, query["start_date"], query["end_date"])
        return [record.to_json() for record in records]
    except ValueError as e:
        abort(400, message=str(e))
