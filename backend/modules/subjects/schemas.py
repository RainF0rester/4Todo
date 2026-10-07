from apiflask import Schema
from apiflask.fields import Integer, String, DateTime, UUID


class SubjectSchema(Schema):
    id = UUID()
    user_id = Integer()
    name = String()
    description = String(allow_none=True)
    start_time = DateTime(allow_none=True)
    finish_time = DateTime(allow_none=True)
    created_at = DateTime()
    updated_at = DateTime()

class SubjectCreateSchema(Schema):
    name = String(required=True)
    description = String(allow_none=True)
    start_time = DateTime(required=False, allow_none=True)
    finish_time = DateTime(required=False, allow_none=True)

class SubjectUpdateSchema(Schema):
    name = String(required=False)
    description = String(allow_none=True)
    start_time = DateTime(required=False, allow_none=True)
    finish_time = DateTime(required=False, allow_none=True)