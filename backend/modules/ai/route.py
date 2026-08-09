from apiflask import APIBlueprint
from flask import g

from . import service
from backend.db import get_session
from backend.utils.auth_decorator import require_auth
from backend.modules.ai.schmas import AskSchema, ReplySchema

bp = APIBlueprint("ai", __name__, url_prefix="/ai",tag="ai")

@bp.post("/ask")
@require_auth
@bp.input(AskSchema)
@bp.output(ReplySchema)
@bp.doc(security=[{"BearerAuth": []}])
def ai_ask(json_data):
    session = get_session()
    user_id = int(g.user_id)
    reply = service.ask(json_data["prompt"], session, user_id)
    return {"reply": reply}