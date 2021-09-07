from flask import request
from marshmallow import ValidationError
from flask_restful import Resource, abort, reqparse

from app import db
from schemas.event import event_schema, event_list_schema
from models.event import Event

events_post_args = reqparse.RequestParser()
events_post_args.add_argument('title', type=str, help='Title of the event is required', required=True)
events_post_args.add_argument('date', type=str, help='Date of the event in format \'YEAR-MONTH-DAY HOURS:MINUTES\' '
                                                     'is required', required=True)
events_post_args.add_argument('description', type=str, help='Description of the event')

class EventsListAPIView(Resource):
    def get(self):
        events = Event.query.all()
        return event_list_schema.dump(events)

    def post(self):
        args = events_post_args.parse_args()
        try:
            data = event_schema.load(args)
        except ValidationError as err:
            return err.messages, 422
        new_event = Event(title=data.get('title'), date=data.get('date'), description=data.get('description'),
                          status_code=2)
        db.session.add(new_event)
        db.session.commit()
        return event_schema.dump(new_event), 201


class EventDetailAPIView(Resource):
    def get(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, message='Event does not exist or has been deleted.')
        return event_schema.dump(event), 200

    def patch(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, message='Event does not exist or has been deleted.')

        json_data = request.get_json()
        for key, value in json_data.items():
            if value:
                setattr(event, key, value)

        db.session.commit()
        return event_schema.dump(event), 200

    def delete(self, event_id):
        event = Event.query.get(event_id)
        if not event:
            abort(404, message='Event does not exist or has been deleted.')
        db.session.delete(event)
        db.session.commit()
        return {'message': 'Event deleted successfully'}, 200