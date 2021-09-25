from datetime import datetime

from app import ma
from models.event import Event, EventInvitedGuest
from marshmallow import fields, validate, validates, ValidationError

from .event_status import event_status_schema
from .user import user_schema


class GuestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventInvitedGuest

    first_name = fields.Str()
    last_name = fields.Str()
    category = fields.Str()


class EventSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Event
        load_instance = True

    id = ma.auto_field(dump_only=True)
    title = fields.Str(validate=[validate.Length(min=1, max=500)])
    date = fields.DateTime(format='%Y-%m-%d %H:%M')
    description = fields.Str(validate=[validate.Length(max=5000)])
    status_code = fields.Int()
    status = ma.Nested(event_status_schema, dump_only=True)
    organizer = ma.Nested(user_schema, exclude=('email',), dump_only=True)
    invited_guests = ma.Nested(GuestSchema, many=True)

    @validates('date')
    def is_in_future(self, date):
        if date <= datetime.now():
            raise ValidationError('You cannot create an event with a past date.')


event_create_schema = EventSchema(only=('title', 'description', 'date', 'status_code'))
event_update_schema = EventSchema(only=('title', 'date', 'description', 'status_code', 'invited_guests'))
event_detail_schema = EventSchema(exclude=('status_code',))
event_list_schema = EventSchema(only=('title', 'date', 'status'), many=True)


