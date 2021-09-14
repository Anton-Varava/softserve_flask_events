import jwt

from flask import request, make_response, jsonify

from app import app
from models.user import User

def token_required(func):
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return make_response(jsonify({'message': 'Token is invalid!'}), 401)
        return func(current_user=current_user, *args, **kwargs)

    return decorated