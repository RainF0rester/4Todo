from apiflask import APIBlueprint, abort
from flask import g
from db import get_session
from . import service
from .schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema, StatusSchema
from utils.auth_decorator import require_auth
from modules.tasks.service import cleanup_deleted_tasks

bp = APIBlueprint("tasks", __name__, url_prefix="/tasks", tag="Tasks")


@bp.post("")
@bp.input(TaskCreateSchema)
@bp.output(TaskSchema, status_code=201)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def create_task(json_data):
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        task = service.create_task(session, json_data, user_id=user_id)
        return task.to_dict()
    except ValueError as e:
        abort(400, message=str(e))


@bp.get("/<int:task_id>")
@bp.output(TaskSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_task(task_id: int):
    session = get_session()
    cleanup_deleted_tasks(session)
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        task = service.get_task(session, task_id, user_id=user_id)
        return task.to_dict()
    except ValueError as e:
        return abort(400, message=str(e))


@bp.patch("/<int:task_id>")
@bp.input(TaskUpdateSchema)
@bp.output(TaskSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def update_task(task_id: int, json_data):
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        task = service.update_task(session, task_id, json_data, user_id=user_id)
        return task.to_dict()
    except ValueError as e:
        abort(400, message=str(e))


@bp.patch("/<int:task_id>/delete")
@bp.output(StatusSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def delete_task(task_id: int):
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        service.soft_delete_task(session, task_id, user_id=user_id)
        return {"status": "ok"}
    except ValueError as e:
        return abort(400, message=str(e))


@bp.patch("/<int:task_id>/restore")
@bp.output(StatusSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def restore_task(task_id: int):
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        service.restore_task(session, task_id, user_id=user_id)
        return {"status": "ok"}
    except ValueError as e:
        return abort(400, message=str(e))


@bp.get("")
@bp.output(TaskSchema(many=True))
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def list_tasks():
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        tasks = service.list_tasks(session, include_deleted=False, user_id=user_id)
        return [t.to_dict() for t in tasks]
    except ValueError as e:
        return abort(400, message=str(e))

@bp.get("/deleted")
@bp.output(TaskSchema(many=True))
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def list_deleted_tasks():
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        tasks = service.list_deleted_tasks(session, user_id=user_id)
        return [t.to_dict() for t in tasks]
    except ValueError as e:
        return abort(400, message=str(e))

@bp.patch("<int:task_id>/pin")
@bp.output(StatusSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def pin_task(task_id: int):
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        service.pin_task(session, task_id, user_id=user_id)
        return {"status": "ok"}
    except ValueError as e:
        return abort(400, message=str(e))

@bp.patch("<int:task_id>/unpin")
@bp.output(StatusSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def unpin_task(task_id: int):
    session = get_session()
    try:
        user_id = int(g.user_id)
        if user_id is None:
            abort(401, message="Missing user_id from request")
        service.unpin_task(session, task_id, user_id=user_id)
        return {"status": "ok"}
    except ValueError as e:
        return abort(400, message=str(e))
