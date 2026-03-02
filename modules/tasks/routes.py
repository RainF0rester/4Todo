from flask import Blueprint, request, jsonify
from db import get_session
from . import service

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@bp.post("")
def create_task():
    payload = request.get_json(silent=True) or {}
    session = get_session()
    try:
        task = service.create_task(session, payload)
        return jsonify(task.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.get("/<int:task_id>")
def get_task(task_id: int):
    session = get_session()
    try:
        task = service.get_task(session, task_id)
        return jsonify(task.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400