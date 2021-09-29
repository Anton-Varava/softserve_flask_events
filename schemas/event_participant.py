from marshmallow import fields

from app import ma
from models.event_participant import EventParticipant
from models.participant_status import ParticipantStatus


class ParticipantStatusSchema(ma.SQLAlchemySchema):
    class Meta:
        model = ParticipantStatus

    code = fields.Int()
    title = fields.Str()


class EventParticipantSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventParticipant

    id = fields.Int(dump_only=True)
    event_id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    status_code = fields.Int()
    status = ma.Nested(ParticipantStatusSchema)


participant_detail_schema = EventParticipantSchema(only=('event_id', 'status'))
participant_list_schema = EventParticipantSchema(many=True)
