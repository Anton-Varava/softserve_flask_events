from flask import request, make_response, jsonify
from marshmallow import ValidationError
from flask_restful import Resource, abort, reqparse

from app import db
from schemas.event import event_schema, event_list_schema
from models.event import Event
from .user import token_required

events_post_args = reqparse.RequestParser()
events_post_args.add_argument('title', type=str, help='Title of the event is required', required=True)
events_post_args.add_argument('date', type=str, help='Date of the event in format \'YEAR-MONTH-DAY HOURS:MINUTES\' '
                                                     'is required', required=True)
events_post_args.add_argument('description', type=str, help='Description of the event')


class EventsListAPIView(Resource):
    @token_required
    def get(self, *args, **kwargs):
        events = Event.query.all()
        return event_list_schema.dump(events)

    @token_required
    def post(self, *args, **kwargs):
        json_data = events_post_args.parse_args()
        try:
            data = event_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 422

        current_user = kwargs.get('current_user')
        new_event = Event(title=data.get('title'), date=data.get('date'), description=data.get('description'),
                          organizer_id=current_user.id)
        db.session.add(new_event)
        db.session.commit()
        return event_schema.dump(new_event), 201


class EventDetailAPIView(Resource):
    @token_required
    def get(self, *args, **kwargs):
        event = Event.query.get(kwargs.get('event_id'))
        if not event:
            abort(404, message='Event does not exist or has been deleted.')
        return event_schema.dump(event), 200

    @token_required
    def patch(self, *args, **kwargs):
        event = Event.query.get(kwargs.get('event_id'))
        if not event:
            abort(404, message='Event does not exist or has been deleted.')
        if event.organizer_id != kwargs.get('current_user').id:
            abort(403, message='You don\'t have a permissions to do this.')
        json_data = request.get_json()
        for key, value in json_data.items():
            if value:
                setattr(event, key, value)
        try:
            db.session.commit()
        except:
            abort(422, message='Data is not valid!')
        return event_schema.dump(event), 200

    @token_required
    def delete(self, *args, **kwargs):
        event = Event.query.get(kwargs.get('event_id'))
        if not event:
            abort(404, message='Event does not exist or has been deleted.')
        if event.organizer_id != kwargs.get('current_user').id:
            abort(403, message='You don\'t have a permissions to do this.')
        db.session.delete(event)
        db.session.commit()
        return make_response(jsonify({'message': 'Event deleted successfully'}), 200)
