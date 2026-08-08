from apiflask import APIBlueprint
from backend.utils.auth_decorator import require_auth

from . import service
from backend.modules.ai.schmas import AskSchema, ReplySchema

bp = APIBlueprint("ai", __name__, url_prefix="/ai",tag="ai")

@bp.post("/ask")
@require_auth
@bp.input(AskSchema)
@bp.output(ReplySchema)
@bp.doc(security=[{"BearerAuth": []}])
def ai_ask(json_data):
    reply = service.ask(json_data["prompt"])
    return {"reply": reply}