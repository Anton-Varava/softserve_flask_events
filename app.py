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

from models.event import Event
from models.user import User
from resources.event import EventsListAPIView, EventDetailAPIView
from resources.user import UserAPIView, UserDetailAPIView

api.add_resource(EventsListAPIView, '/events')
api.add_resource(EventDetailAPIView, '/events/<int:event_id>')
api.add_resource(UserAPIView, '/users')
api.add_resource(UserDetailAPIView, '/users/<int:user_id>')


