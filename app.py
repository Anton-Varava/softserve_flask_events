import requests

from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

from flask_restful import Api

from flask_migrate import Migrate

from flask_jwt_extended import JWTManager

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from flask_apispec.extension import FlaskApiSpec

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)
# app.config.update({
#     'APISPEC_SPEC': APISpec(
#         title='Events Flask',
#         version='v1',
#         plugins=[MarshmallowPlugin()],
#         openapi_version='2.0.0'
#     ),
#     'APISPEC_SWAGGER_URL': '/swagger',
#     'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
# })
# docs = FlaskApiSpec(app)
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

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

# docs.register(EventsListAPIView)

api.add_resource(LoginAPIView, '/login')
api.add_resource(UserAPIView, '/users')
api.add_resource(UserDetailAPIView, '/users/<int:user_id>')
api.add_resource(EventsListAPIView, '/events')
api.add_resource(EventDetailAPIView, '/events/<int:event_id>')
api.add_resource(EventRegistration, '/events/<int:event_id>/participants')
api.add_resource(EventStatusAPIView, '/events/statuses')
