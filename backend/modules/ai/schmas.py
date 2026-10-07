from apiflask.schemas import Schema
from marshmallow.fields import String, List, Dict


class AskSchema(Schema):
    prompt = String(required=True)


class ReplySchema(Schema):
    reply = String()


class ConversationSchema(Schema):
    id = String()
    title = String()
    created_at = String()
    updated_at = String()


class ConversationDetailSchema(Schema):
    id = String()
    title = String()
    messages = List(Dict())
    created_at = String()
    updated_at = String()