import json

import requests
from app import db
from flask import jsonify


class APISource(db.Model):
    __tablename__ = 'api_sources'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=True)
    source_url = db.Column(db.String, nullable=False)
    artefacts_source_url = db.Column(db.String, nullable=True)
    authentication_source_url = db.Column(db.String, nullable=True)
    source_login = db.Column(db.String, nullable=True)
    source_password = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Api Source {self.title} (№{self.id}). Category - {self.category}>'

    @property
    def token(self):
        return self._get_token()

    def _get_token(self):
        response_data = requests.post(self.authentication_source_url,
                                      headers={'Content-type': 'application/json'},
                                      json={'user': {
                                          'username': self.source_login,
                                          'password': self.source_password}
                                      })
        token = response_data.json().get('user').get('token')
        return token





