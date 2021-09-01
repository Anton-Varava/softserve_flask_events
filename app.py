from flask_sqlalchemy import SQLAlchemy
from flask import Flask


from config import Configuration

from events.blueprint import events

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)

from events.models import Event

app.register_blueprint(events, url_prefix='/events')



