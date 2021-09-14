import requests
from flask import request, make_response, jsonify
from marshmallow import ValidationError
from flask_restful import Resource, abort, reqparse

from app import db
from schemas.event import event_schema, event_list_schema
from models.event import Event, EventInvitedGuest
from models.api_source import APISource
from .authentocation import token_required

events_post_args = reqparse.RequestParser()
events_post_args.add_argument('title', type=str, help='Title of the event is required', required=True)
events_post_args.add_argument('date', type=str, help='Date of the event in format \'YEAR-MONTH-DAY HOURS:MINUTES\' '
                                                     'is required', required=True)
events_post_args.add_argument('description', type=str, help='Description of the event')


class EventsListAPIView(Resource):
    @token_required
    def get(self, *args, **kwargs):
        query_params = request.args
        if query_params:
            params = {}
            for attr, value in query_params.items():
                if any([attr == 'title', attr == 'date', attr == 'status_code', attr == 'organizer_id']):
                    params[attr] = value
            events = Event.query.filter_by(**params).all()
        else:
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
            if key == 'guests':
                guests_data = self.get_guests_data(value)
                if guests_data:
                    for guest_data in guests_data:
                        new_guest = EventInvitedGuest(first_name=guest_data.get('first_name'),
                                                      last_name=guest_data.get('last_name'),
                                                      category=guest_data.get('category'),
                                                      event_id=event.id)
                        db.session.add(new_guest)
            elif value:
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

    @staticmethod
    def get_guests_data(guests_json_data):
        guests_data = []
        for guest in guests_json_data:
            source_category = guest.get('category')
            guest_first_name = guest.get('first_name')
            guest_last_name = guest.get('last_name')
            api_sources = APISource.query.filter_by(category=source_category).all()
            for source in api_sources:
                # looking for the first match. Break if guest is founded
                url = source.source_url
                authorization_token = f'Token {source.token}'
                headers = {'Content-type': 'application/json',
                           'Authorization': authorization_token}

                response = requests.get(url,
                                        headers=headers,
                                        params={'first_name': guest_first_name,
                                                'last_name': guest_last_name})
                response_guest_data = response.json().get('authors')[0]
                if response_guest_data:
                    guests_data.append({'category': source_category,
                                        'first_name': response_guest_data.get('first_name'),
                                        'last_name': response_guest_data.get('last_name')})

                    break
        return guests_data

