from app import ma
from models.event import Event


class EventSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Event

    id = ma.auto_field()
    title = ma.auto_field()
    date = ma.auto_field()
    description = ma.auto_field()
    status_code = ma.auto_field()
    organizer_id = ma.auto_field()


event_schema = EventSchema()
event_list_schema = EventSchema(many=True, only=('id', 'title', 'date'))