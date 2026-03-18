from apiflask import Schema
from apiflask.fields import Integer, String, List, Boolean

class TaskSchema(Schema):
    id = Integer()
    task_title = String()
    task_due = String(allow_none=True)
    task_description = String(allow_none=True)
    task_level = Integer()
    is_finished = Integer()

class TaskCreateSchema(Schema):
    task_title = String()
    task_due = String()
    task_description = String()
    task_level = Integer()

class StatusSchema(Schema):
    status = String()
    message = String()