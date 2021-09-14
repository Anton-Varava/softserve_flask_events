from app import app, db
from models.user import User
from schemas.user import user_schema, user_list_schema
from config import Configuration

from flask_restful import Resource, abort, reqparse
from flask import request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from datetime import datetime, timedelta
from .authentocation import token_required

class LoginAPIView(Resource):
    def post(self):
        json_data = request.get_json()
        email_from_json = json_data.get('email')
        password_from_json = json_data.get('password')

        # returns 401 if any email or password is missing
        if not json_data or not email_from_json or not password_from_json:
            return make_response(jsonify({'message': 'Email and password fields in required.'}), 401)

        user = User.query.filter_by(email=email_from_json).first()
        # returns 401 if user does not exist
        if not user:
            return make_response(jsonify({'message': 'User does not exist.'}), 401)

        # returns 403 if password is wrong
        if not check_password_hash(user.password, password_from_json):
            return make_response(jsonify({'message': 'Wrong password.'}), 403)

        # generates the JWT Token
        token = jwt.encode({
            'id': user.id,
            'exp': datetime.now() + timedelta(days=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return make_response(jsonify({'token': token}), 201)


class UserAPIView(Resource):
    # Sign Up User
    def post(self):
        data = request.get_json()
        hashed_password = generate_password_hash(data.get('password'), method='sha256')
        new_user = User(first_name=data.get('first_name'),
                        second_name=data.get('second_name'),
                        email=data.get('email'),
                        password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return user_schema.dump(new_user), 201

    @token_required
    def get(self, **kwargs):
        users = User.query.all()
        return user_list_schema.dump(users), 200


class UserDetailAPIView(Resource):
    @token_required
    def get(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')
        user = User.query.get(user_id_requested)
        if not user:
            abort(404, message='User does not exist or has been deleted.')
        return user_schema.dump(user), 200

    @token_required
    def patch(self, *args, **kwargs):
        current_user = kwargs.get('current_user')
        user_id_requested = kwargs.get('user_id')
        if current_user.id != user_id_requested:
            abort(403, message='You can\'t to edit this user.')
        user = User.query.get(user_id_requested)
        if not user:
            abort(404, message='User does not exist or has been deleted.')

        json_data = request.get_json()
        for key, value in json_data.items():
            if value:
                setattr(user, key, value)

        db.session.commit()
        return user_schema.dump(user), 200

    @token_required
    def delete(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')
        current_user = kwargs.get('current_user')
        user = User.query.filter(id=user_id_requested).first()
        if not user:
            abort(404, message='User does not exist or has been deleted.')
        if user_id_requested != current_user.id:
            abort(403, message='You don\'t have a permissions to delete this user.')
        db.session.delete(user)
        db.session.commit()

        return make_response(jsonify({'message': 'User deleted successfully'}, 200))



