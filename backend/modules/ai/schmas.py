from apiflask.schemas import Schema
from marshmallow.fields import String

class AskSchema(Schema):
    prompt = String(required=True)

class ReplySchema(Schema):
    reply = String()