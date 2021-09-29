from flask_restful import Resource, abort
from flask import request, make_response, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_apispec import marshal_with, use_kwargs, doc
from flask_apispec.views import MethodResource
from marshmallow import fields

from app import db
from models.event_participant import EventParticipant
from models.event import Event
from models.participant_status import ParticipantStatus
from models.user import User
from schemas.event_participant import participant_detail_schema, participant_list_schema
from schemas.subsidiary import MessageResponseSchema


@doc(tags=['Events'])
class EventRegistration(MethodResource, Resource):
    @jwt_required()
    @marshal_with(participant_detail_schema)
    @doc(description='Get a registration details of an event.')
    def get(self, *args, **kwargs):
        event_id = kwargs.get('event_id')

        event_registration_instance = EventParticipant.query.filter_by(event_id=event_id, user_id=get_jwt_identity()).\
            first_or_404(description='You are not registered for this event yet.')

        return event_registration_instance, 200

    @jwt_required()
    @marshal_with(MessageResponseSchema, 201)
    @doc(description='Register for an event.')
    def post(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        event = Event.query.get_or_404(event_id, description='Event does not exist or has been deleted.')

        if not event.is_current:
            abort(409, message='You can not to register on the event. Maybe, event has already passed or canceled.')

        current_user = User.query.get_or_404(get_jwt_identity())

        if EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).first():
            abort(409, message='You are already registered for this event')

        try:
            participant_status = ParticipantStatus.query.get(request.get_json().get('status_code'))
        except:
            participant_status = None

        if participant_status:
            new_participant = EventParticipant(event_id=event_id, user_id=current_user.id, status_code=participant_status)
        else:
            new_participant = EventParticipant(event_id=event_id, user_id=current_user.id)
        db.session.add(new_participant)
        db.session.commit()

        return {'message': 'You have successfully registered for the event.'}, 200

    @jwt_required()
    @use_kwargs({'status_code': fields.Int()})
    @marshal_with(participant_detail_schema, 200)
    @doc(description='Change a status of a event registration.')
    def patch(self, *args, **kwargs):
        new_status = ParticipantStatus.query.get_or_404(request.get_json().get('status_code'),
                                                        description='Invalid status code.')
        event_id = kwargs.get('event_id')
        current_user = User.query.get_or_404(get_jwt_identity())

        event_registration_instance = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).\
            first_or_404(description='You are not registered for this event yet.')

        setattr(event_registration_instance, 'status_code', new_status.code)
        db.session.commit()

        return event_registration_instance, 200

    @jwt_required()
    @marshal_with(MessageResponseSchema, 200)
    @doc(description='Delete a registration of an event.')
    def delete(self, *args, **kwargs):
        event_id = kwargs.get('event_id')
        current_user = User.query.get_or_404(get_jwt_identity())

        event_registration_instance = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id). \
            first_or_404(description='You are not registered for this event yet.')

        db.session.delete(event_registration_instance)
        db.session.commit()

        return {'message': 'Registration on event deleted successfully.'}, 200


