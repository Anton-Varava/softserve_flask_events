from app import ma
from models.event_status import EventStatus
from marshmallow import fields


class EventStatusSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventStatus
        load_instance = True

    code = fields.Int()
    title = fields.Str()


event_status_schema = EventStatusSchema()
event_list_status_schema = EventStatusSchema(many=True)
