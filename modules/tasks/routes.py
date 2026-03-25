from apiflask import APIBlueprint, abort
from db import get_session
from . import service
from .schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema, StatusSchema

bp = APIBlueprint("tasks", __name__, url_prefix="/tasks", tag="Tasks")


@bp.post("")
@bp.input(TaskCreateSchema)
@bp.output(TaskSchema, status_code=201)
def create_task(json_data):
    session = get_session()
    try:
        task = service.create_task(session, json_data)
        return task.to_dict()
    except ValueError as e:
        abort(400, message=str(e))


@bp.get("/<int:task_id>")
@bp.output(TaskSchema)
def get_task(task_id: int):
    session = get_session()
    try:
        task = service.get_task(session, task_id)
        return task.to_dict()
    except ValueError as e:
        return abort(400, message=str(e))


@bp.patch("/<int:task_id>")
@bp.input(TaskUpdateSchema)
@bp.output(TaskSchema)
def update_task(task_id: int, json_data):
    session = get_session()
    try:
        task = service.update_task(session, task_id, json_data)
        return task.to_dict()
    except ValueError as e:
        abort(400, message=str(e))


@bp.patch("/<int:task_id>/delete")
@bp.output(StatusSchema)
def delete_task(task_id: int):
    session = get_session()
    try:
        service.soft_delete_task(session, task_id)
        return {"status": "ok"}
    except ValueError as e:
        return abort(400, message=str(e))


@bp.patch("/<int:task_id>/restore")
@bp.output(StatusSchema)
def restore_task(task_id: int):
    session = get_session()
    try:
        service.restore_task(session, task_id)
        return {"status": "ok"}
    except ValueError as e:
        return abort(400, message=str(e))


@bp.get("")
@bp.output(TaskSchema(many=True))
def list_tasks():
    session = get_session()
    try:
        tasks = service.list_tasks(session, include_deleted=False)
        return [t.to_dict() for t in tasks]
    except ValueError as e:
        return abort(400, message=str(e))