from werkzeug.security import generate_password_hash, check_password_hash

from flask_restful import Resource, abort

from flask_jwt_extended import jwt_required, get_jwt_identity, create_refresh_token, create_access_token

from flask import request, jsonify, make_response

from app import db
from models.user import User
from schemas.user import user_schema, user_list_schema


class LoginAPIView(Resource):
    # Sign In User
    def post(self):
        try:
            json_data = request.get_json()
        except:
            abort(400, message='There is no JSON data in the request')

        email_from_json = json_data.get('email')
        password_from_json = json_data.get('password')

        # raise 400 if an email or a password is missing
        if not email_from_json or not password_from_json:
            abort(400, message='Email and password fields in required.')

        # raise 404 if user does not exist
        user = User.query.filter_by(email=email_from_json).first_or_404(description='User does not exist.')

        # raise 401 if password is wrong
        if not check_password_hash(user.password, password_from_json):
            abort(401, message='Wrong password.')

        return make_response(jsonify(email=user.email,
                                     access_token=create_access_token(identity=user.id, fresh=True),
                                     refresh_token=create_refresh_token(identity=user.id)), 200)


class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        new_access_token = create_access_token(identity=get_jwt_identity(), fresh=False)
        return make_response(jsonify(access_token=new_access_token), 200)


class UserAPIView(Resource):
    # Sign Up User
    def post(self):
        try:
            json_data = request.get_json()
        except:
            abort(400, message='There is no JSON data in the request')

        email_from_json = json_data.get('email')
        password_from_json = json_data.get('password')
        first_name_from_json = json_data.get('first_name')

        if not email_from_json or not password_from_json or not first_name_from_json:
            abort(400, message='Email and password fields in required.')

        if User.query.filter_by(email=email_from_json).first():
            abort(409, message='User with this email already exists.')

        hashed_password = generate_password_hash(password_from_json, method='sha256')
        new_user = User(first_name=first_name_from_json,
                        second_name=json_data.get('second_name'),
                        email=email_from_json,
                        password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return user_schema.dump(new_user), 201


class UserDetailAPIView(Resource):
    @jwt_required()
    def get(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')
        user = User.query.get_or_404(user_id_requested, description='User does not exist or has been deleted.')
        return user_schema.dump(user), 200

    @jwt_required(fresh=True)
    def patch(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')

        user = User.query.get_or_404(user_id_requested, description='User does not exist or has been deleted.')

        if get_jwt_identity() != user.id:
            abort(403, message='You can\'t to edit this user.')

        json_data = request.get_json()
        for key, value in json_data.items():
            if value:
                setattr(user, key, value)

        db.session.commit()
        return user_schema.dump(user), 200

    @jwt_required(fresh=True)
    def delete(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')

        user = User.query.filter(id=user_id_requested).\
            first_or_404(description='User does not exist or has been deleted.')

        if user.id != get_jwt_identity():
            abort(403, message='You don\'t have a permissions to delete this user.')

        db.session.delete(user)
        db.session.commit()
        return make_response(jsonify({'message': 'User deleted successfully'}, 200))



