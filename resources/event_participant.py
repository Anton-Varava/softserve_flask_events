from flask_restful import Resource, abort
from flask import request, make_response, jsonify

from app import db
from models.event_participant import EventParticipant
from models.event import Event
from models.participant_status import ParticipantStatus
from schemas.event_participant import participant_schema, participant_list_schema
from .authentication import token_required


class EventRegistration(Resource):
    @token_required
    def get(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        current_user = kwargs.get('current_user')

        event_registration_instance = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).\
            first_or_404(description='You are not registered for this event yet.')

        return participant_schema.dump(event_registration_instance)


    @token_required
    def post(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        event = Event.query.get_or_404(event_id, description='Event does not exist or has been deleted.')

        if not event.is_current:
            abort(409, message='You can not to register on the event. Maybe, event has already passed or canceled.')

        current_user = kwargs.get('current_user')

        if EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).first():
            abort(409, message='You are already registered for this event')
            
        try:
            participant_status = ParticipantStatus.query.get(request.get_json().get('status'))
        except:
            participant_status = None

        if participant_status:
            new_participant = EventParticipant(event_id=event_id, user_id=current_user.id, status=participant_status)
        else:
            new_participant = EventParticipant(event_id=event_id, user_id=current_user.id)
        db.session.add(new_participant)
        db.session.commit()

        return make_response(jsonify({'message': 'You have successfully registered for the event.'}))


    @token_required
    def patch(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        current_user = kwargs.get('current_user')
        try:
            status_field = int(request.get_json().get('status'))
        except:
            abort(400, message='Status field is required. Should be a number.')

        event_registration_instance = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).\
            first_or_404(description='You are not registered for this event yet.')

        new_status = ParticipantStatus.query.get_or_404(status_field, description='Invalid status code.')
        setattr(event_registration_instance, 'status', new_status.code)
        db.session.commit()

        return participant_schema.dump(event_registration_instance)


    @token_required
    def delete(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        current_user = kwargs.get('current_user')

        event_registration_instance = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id). \
            first_or_404(description='You are not registered for this event yet.')

        db.session.delete(event_registration_instance)
        db.session.commit()

        return make_response(jsonify({'message': 'Registration on event deleted successfully.'}))


