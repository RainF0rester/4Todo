from apiflask.schemas import Schema
from marshmallow.fields import Integer, String


class PomodoroSchema(Schema):
    id = Integer()
    user_id = Integer()
    date = String()
    count = Integer()

class PomodoroRangeQuerySchema(Schema):
    start_date = String()
    end_date = String()