from flask_restful import Resource
from flask import request, abort, make_response, jsonify

from app import db
from models.event_participant import EventParticipant
from models.event import Event
from schemas.event_participant import participant_schema, participant_list_schema
from .user import token_required


class EventRegistration(Resource):
    @token_required
    def get(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        current_user = kwargs.get('current_user')

        event_registration_data = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).first()

        if not event_registration_data:
            abort(404, 'You are not registered for this event yet.')

        return participant_schema.dump(event_registration_data)


    @token_required
    def post(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        event = Event.query.get(event_id)
        if not event:
            abort(404, 'Event does not exist or has been deleted.')
        # if not event.is_current:
        #     abort(403, 'Event has already passed or canceled.')

        current_user = kwargs.get('current_user')

        if EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id):
            abort(409, 'You are already registered for this event')

        new_participant = EventParticipant(event_id=event_id, user_id=current_user.id)

        db.session.add(new_participant)
        db.session.commit()

        return make_response(jsonify({'message': 'You have successfully registered fot the event.'}))



