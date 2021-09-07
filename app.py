from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

from flask_marshmallow import Marshmallow
from marshmallow import ValidationError

from flask_restful import Api, Resource, reqparse, abort

from flask_migrate import Migrate

from config import Configuration

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
api = Api(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

from models.event import Event
from resources.event import EventsListAPIView, EventDetailAPIView

api.add_resource(EventsListAPIView, '/events')
api.add_resource(EventDetailAPIView, '/events/<int:event_id>')

