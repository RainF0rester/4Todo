import threading
from flask import request, current_app
from flask_socketio import emit, disconnect
from backend.db import get_session
from backend.utils.jwt_utils import validate_token, TokenError
from backend.modules.ai import service

# sid as key, store Event and result
confirm_events: dict[str, threading.Event] = {}
confirm_results: dict[str, bool] = {}


def _get_user_id_from_token(token: str) -> int | None:
    try:
        result = validate_token(token)
        if result["state"] == "refreshable":
            return None
        return int(result["payload"]["user_id"])
    except TokenError:
        return None


def register_handlers(socketio):

    @socketio.on("ai_chat")
    def handle_chat(data):
        token = data.get("token", "")
        prompt = data.get("prompt", "")

        user_id = _get_user_id_from_token(token)
        if not user_id:
            emit("ai_error", {"error": "Unauthorized"})
            disconnect()
            return

        session = get_session()
        sid = request.sid

        # callback function
        def confirm_callback(tool_name: str, tool_input: dict) -> bool:

            #create a event
            event = threading.Event()
            confirm_events[sid] = event
            confirm_results[sid] = False

            # send confirm request
            socketio.emit("confirm_required", {
                "tool": tool_name,
                "input": tool_input
            }, to=sid)

            timed_out = not event.wait(timeout=30)
            if timed_out:
                return False
            return confirm_results.get(sid, False)

        app = current_app._get_current_object()

        def run_agent():
            try:
                with app.app_context():
                    reply = service.ask(prompt, session, user_id, confirm_callback=confirm_callback)
                    socketio.emit("ai_reply", {"reply": reply}, to=sid)
            except Exception as e:
                socketio.emit("ai_error", {"error": str(e)}, to=sid)

        socketio.start_background_task(run_agent)

    @socketio.on("confirm")
    def handle_confirm(data):
        sid = request.sid
        confirm_results[sid] = data.get("confirmed", False)
        event = confirm_events.pop(sid, None)
        if event:
            event.set()
