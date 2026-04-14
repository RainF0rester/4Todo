from apiflask import Schema
from apiflask.fields import Integer, String

class TaskSchema(Schema):
    id = Integer()
    task_title = String()
    task_due = String(allow_none=True)
    task_description = String(allow_none=True)
    task_level = Integer()
    is_finished = Integer()
    is_pinned = Integer()

class TaskCreateSchema(Schema):
    task_title = String(required=True)
    task_due = String(required=False, allow_none=True)
    task_description = String(allow_none=True)
    task_level = Integer(required=True)
    is_pinned = Integer(required=False)

class TaskUpdateSchema(Schema):
    task_title = String(required=False)
    task_due = String(required=False, allow_none=True)
    task_description = String(required=False, allow_none=True)
    task_level = Integer(required=False)
    is_finished = Integer(required=False, allow_none=True)
    is_pinned = Integer(required=False, allow_none=True)

class StatusSchema(Schema):
    status = String()
    message = String()