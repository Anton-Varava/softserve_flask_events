from app import ma
from models.event_status import EventStatus


class EventStatusSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventStatus

    code = ma.auto_field()
    title = ma.auto_field()


event_status_schema = EventStatusSchema()
event_list_status_schema = EventStatusSchema(many=True)
