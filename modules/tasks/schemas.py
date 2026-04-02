from apiflask import Schema
from apiflask.fields import Integer, String

class TaskSchema(Schema):
    id = Integer()
    task_title = String()
    task_due = String(allow_none=True)
    task_description = String(allow_none=True)
    task_level = Integer()
    is_finished = Integer()

class TaskCreateSchema(Schema):
    task_title = String(required=True)
    task_due = String(allow_none=True)
    task_description = String(allow_none=True)
    task_level = Integer(required=True)

class TaskUpdateSchema(Schema):
    task_title = String(required=False)
    task_due = String(required=False, allow_none=True)
    task_description = String(required=False, allow_none=True)
    task_level = Integer(required=False)
    is_finished = Integer(required=False)

class StatusSchema(Schema):
    status = String()
    message = String()