from apiflask import Schema
from apiflask.fields import Integer, String, Nested

class UserSchema(Schema):
    id = Integer()
    username = String()
    email = String()

class RegisterReqSchema(Schema):
    email = String(required=True)
    username = String(required=True)
    password = String(required=True)

class RegisterRespSchema(Schema):
    user = Nested(UserSchema)

class LoginReqSchema(Schema):
    identity = String(required=True)
    password = String(required=True)

class LoginRespSchema(Schema):
    user = Nested(UserSchema)
    token = String()

