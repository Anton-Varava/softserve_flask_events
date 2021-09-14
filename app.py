import requests

from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

from flask_restful import Api

from flask_migrate import Migrate

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

from models.event import Event, EventInvitedGuest
from models.user import User
from models.event_status import EventStatus
from models.event_participant import EventParticipant
from models.participant_status import ParticipantStatus
from models.api_source import APISource
from resources.event import EventsListAPIView, EventDetailAPIView
from resources.user import UserAPIView, UserDetailAPIView, LoginAPIView
from resources.event_status import EventStatusAPIView
from resources.event_participant import EventRegistration

api.add_resource(LoginAPIView, '/login')
api.add_resource(UserAPIView, '/users')
api.add_resource(UserDetailAPIView, '/users/<int:user_id>')
api.add_resource(EventsListAPIView, '/events')
api.add_resource(EventDetailAPIView, '/events/<int:event_id>')
api.add_resource(EventRegistration, '/events/<int:event_id>/participants')
api.add_resource(EventStatusAPIView, '/statuses')


@app.route('/api', methods=['GET'])
def django_request():
    url = 'http://127.0.0.1:8000/api/authors/'
    headers = {'Content-type': 'application/json', 'Authorization': 'Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNjMxNjM1NDIzfQ.2mGPCzqUazklHCqMhw8jbLSEIexyNz_VZ0vVXr2b5mA'}
    response = requests.get(url, headers=headers)
    print(response.text)


