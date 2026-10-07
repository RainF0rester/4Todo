from apiflask import APIBlueprint, abort
from flask import g

from backend.db import get_session
from backend.utils.auth_decorator import require_auth
from backend.modules.ai import repo as conv_repo
from backend.modules.ai.schmas import ConversationSchema, ConversationDetailSchema

bp = APIBlueprint("ai", __name__, url_prefix="/ai", tag="ai")


@bp.get("/conversations")
@bp.output(ConversationSchema(many=True))
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def list_conversations():
    session = get_session()
    user_id = int(g.user_id)
    conversations = conv_repo.list_conversations(session, user_id)
    return [c.to_json() for c in conversations]


@bp.get("/conversations/<string:conv_id>")
@bp.output(ConversationDetailSchema)
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_conversation(conv_id: str):
    session = get_session()
    user_id = int(g.user_id)
    import uuid
    try:
        conversation = conv_repo.get_conversation(session, uuid.UUID(conv_id))
    except ValueError:
        abort(400, message="Invalid conversation id")
    if not conversation or conversation.user_id != user_id:
        abort(404, message="Conversation not found")
    return conversation.to_dict()


@bp.delete("/conversations/<string:conv_id>")
@bp.doc(security=[{"BearerAuth": []}])
@require_auth
def delete_conversation(conv_id: str):
    session = get_session()
    user_id = int(g.user_id)
    import uuid
    try:
        conversation = conv_repo.get_conversation(session, uuid.UUID(conv_id))
    except ValueError:
        abort(400, message="Invalid conversation id")
    if not conversation or conversation.user_id != user_id:
        abort(404, message="Conversation not found")
    conv_repo.delete_conversation(session, uuid.UUID(conv_id))
    return {}, 204
