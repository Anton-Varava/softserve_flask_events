from app import ma
from models.event import Event, EventInvitedGuest

from .event_status import event_status_schema
from .user import user_schema


class GuestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventInvitedGuest
        fields = ('first_name', 'last_name', 'category')


class EventSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Event
        load_instance = True
        include_fk = True
        fields = ('id', 'title', 'date', 'description', 'status_code', 'organizer_id', 'invited_guests')

    status_code = ma.Nested(event_status_schema)
    organizer_id = ma.Nested(user_schema, exclude=('email',))
    invited_guests = ma.Nested(GuestSchema, many=True)


event_schema = EventSchema()
event_list_schema = EventSchema(many=True)
