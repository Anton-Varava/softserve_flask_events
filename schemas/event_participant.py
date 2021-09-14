from app import ma
from models.event_participant import EventParticipant


class EventParticipantSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventParticipant

    id = ma.auto_field()
    event_id = ma.auto_field()
    user_id = ma.auto_field()
    status = ma.auto_field()


participant_schema = EventParticipantSchema()
participant_list_schema = EventParticipantSchema(many=True)
