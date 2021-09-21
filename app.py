from datetime import timedelta

from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow

from flask_restful import Api

from flask_migrate import Migrate

from flask_jwt_extended import JWTManager

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)
app.config["JWT_SECRET_KEY"] = app.config['SECRET_KEY']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=3)
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
from resources.user import UserAPIView, UserDetailAPIView, LoginAPIView, RefreshToken
from resources.event_status import EventStatusAPIView
from resources.event_participant import EventRegistration


api.add_resource(LoginAPIView, '/login')
api.add_resource(RefreshToken, '/login/refresh')
api.add_resource(UserAPIView, '/users')
api.add_resource(UserDetailAPIView, '/users/<int:user_id>')
api.add_resource(EventsListAPIView, '/events')
api.add_resource(EventDetailAPIView, '/events/<int:event_id>')
api.add_resource(EventRegistration, '/events/<int:event_id>/participants')
api.add_resource(EventStatusAPIView, '/events/statuses')
