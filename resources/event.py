import requests

from flask_jwt_extended import jwt_required, get_jwt_identity

from marshmallow import ValidationError, fields

from flask_restful import Resource, abort

from flask_apispec import marshal_with, use_kwargs, doc
from flask_apispec.views import MethodResource

from flask import request

from app import db
from schemas.event import GuestSchema, event_create_schema, event_detail_schema, event_list_schema, event_update_schema
from schemas.subsidiary import MessageResponseSchema
from models.event import Event, EventInvitedGuest
from models.event_status import EventStatus
from models.user import User
from models.api_source import APISource


@doc(tags=['Events'])
class EventsListAPIView(MethodResource, Resource):
    @jwt_required()
    @marshal_with(event_list_schema, 200)
    @doc(description='Get list of events.', params={
        'title': {
            'description': 'Title of event.', 'in': 'query', 'type': 'string', 'required': False
        },
        'date': {
            'description': 'Date of event.', 'in': 'query', 'type': 'datetime', 'required': False
        },
        'organizer_id': {
            'description': 'Id of event organizer.', 'in': 'query', 'type': 'integer', 'required': False
        }
    })
    def get(self, *args, **kwargs):
        query_params = request.args

        # Events filtering
        if query_params:
            params = {}
            for attr, value in query_params.items():
                if attr == 'status_code' and value == '10':
                    abort(400, message='Invalid status code.')
                elif any([attr == 'title', attr == 'date', attr == 'organizer_id', attr == 'status_code']):
                    params[attr] = value
            events = Event.query.filter_by(**params).all()
        else:
            events = Event.query.filter(Event.status_code != 10).all()

        if not events:
            abort(404, message='Requested event not found.')
        return events, 200

    @jwt_required()
    @use_kwargs(event_create_schema)
    @marshal_with(event_detail_schema, 201)
    @doc(description='Create a new event.')
    def post(self, *args, **kwargs):
        json_data = request.get_json()
        try:
            new_event = event_create_schema.load(json_data)
        except ValidationError as err:
            abort(400, message=err.messages)

        current_user = User.query.get_or_404(get_jwt_identity())
        new_event.organizer_id = current_user.id
        try:
            db.session.add(new_event)
            db.session.commit()
        except:
            abort(500, message='Something went wrong. Failed to create an event.')
        return new_event, 201

@doc(tags=['Events'])
class EventDetailAPIView(MethodResource, Resource):
    @jwt_required()
    @marshal_with(event_detail_schema, 200)
    @doc(description='Get an event detail.')
    def get(self, *args, **kwargs):
        event = Event.query.get_or_404(kwargs.get('event_id'), description='Event does not exist or has been deleted.')
        if event.is_draft and event.organizer_id != get_jwt_identity():
            abort(404, message='Event does not exist or has been deleted.')
        return event, 200

    @jwt_required()
    @use_kwargs(event_update_schema)
    @marshal_with(event_detail_schema, 200)
    @doc(description='Update an event.')
    def patch(self, *args, **kwargs):
        event = Event.query.get_or_404(kwargs.get('event_id'), description='Event does not exist or has been deleted.')

        if event.organizer_id != get_jwt_identity():
            abort(403, message='You don\'t have a permissions to do this.')

        try:
            json_data = request.get_json()
        except:
            abort(400, message='There is no JSON data in the request')

        for key, value in json_data.items():
            if key == 'invited_guests':
                guests_data = self.get_guests_data(value)
                if guests_data:
                    for guest_data in guests_data:
                        new_guest = EventInvitedGuest(first_name=guest_data.get('first_name'),
                                                      last_name=guest_data.get('last_name'),
                                                      category=guest_data.get('category'),
                                                      event_id=event.id)
                        if not self.guest_is_already_added(new_guest):
                            # Create new Guest if not exist
                            db.session.add(new_guest)
            elif value:
                setattr(event, key, value)
        try:
            db.session.commit()
        except:
            abort(409, message='Data is not valid.')
        return event, 200

    @jwt_required()
    @marshal_with(MessageResponseSchema, 200)
    @doc(description='Delete an event.')
    def delete(self, *args, **kwargs):
        event = Event.query.get_or_404(kwargs.get('event_id'), description='Event does not exist or has been deleted.')
        if event.organizer_id != get_jwt_identity():
            abort(403, message='You don\'t have a permissions to do this.')
        db.session.delete(event)
        db.session.commit()
        return {'message': 'Event deleted successfully.'}, 200

    @staticmethod
    def get_guests_data(guests_json_data) -> list:
        guests_data = []
        for guest in guests_json_data:
            source_category = guest.get('category')
            guest_first_name = guest.get('first_name')
            guest_last_name = guest.get('last_name')
            if source_category:
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
                    try:
                        response_guest_data = response.json().get('authors')[0]
                        if response_guest_data:
                            guests_data.append({'category': source_category,
                                                'first_name': response_guest_data.get('first_name'),
                                                'last_name': response_guest_data.get('last_name')})

                            break
                    except:
                        continue
            else:
                guests_data.append({'category': source_category,
                                    'first_name': guest_first_name,
                                    'last_name': guest_last_name})
        if not guests_data:
            abort(404, message="Guests are not found.")
        return guests_data

    @staticmethod
    def guest_is_already_added(guest) -> bool:
        guest_checking = EventInvitedGuest.query.filter_by(category=guest.category,
                                                           event_id=guest.event_id,
                                                           first_name=guest.first_name,
                                                           last_name=guest.last_name).first()
        if guest_checking:
            return True
        return False
