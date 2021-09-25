from werkzeug.security import generate_password_hash, check_password_hash

from flask_apispec import marshal_with, use_kwargs, doc
from flask_apispec.views import MethodResource

from flask_restful import Resource, abort

from flask_jwt_extended import jwt_required, get_jwt_identity, create_refresh_token, create_access_token

from flask import request

from app import db
from models.user import User
from schemas.user import user_detail_schema, user_login_schema, user_create_schema, \
    login_token_schema, refresh_login_schema, user_update_schema
from schemas.subsidiary import MessageResponseSchema


@doc(tags=['Authentication'])
class LoginAPIView(MethodResource, Resource):

    # Sign In User
    @use_kwargs(user_login_schema)
    @marshal_with(login_token_schema, 200)
    @doc(description='Get authentication tokens. ')
    def post(self, *args, **kwargs):
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

        return {'access_token': create_access_token(identity=user.id, fresh=True),
                'refresh_token': create_refresh_token(identity=user.id),
                'email': user.email}, 200


@doc(tags=['Authentication'])
class RefreshToken(MethodResource, Resource):
    @jwt_required(refresh=True)
    @marshal_with(refresh_login_schema, 200)
    @doc(description='Refresh access token.')
    def post(self, *args, **kwargs):
        new_access_token = create_access_token(identity=get_jwt_identity(), fresh=False)
        return {'access_token': new_access_token}, 200


@doc(tags=['User'])
class UserAPIView(MethodResource, Resource):
    # Sign Up User
    @use_kwargs(user_create_schema)
    @marshal_with(user_detail_schema, 201)
    @doc(description='Create a new user.')
    def post(self, *args, **kwargs):
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

        return new_user, 201


@doc(tags=['User'])
class UserDetailAPIView(MethodResource, Resource):
    @jwt_required()
    @marshal_with(user_detail_schema)
    @doc(description='Get a user details. Available only if is_staff or owner.')
    def get(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')
        current_user = User.query.get_or_404(get_jwt_identity())
        if user_id_requested != current_user.id and not current_user.is_staff:
            return abort(403, message='You don\'t have a permissions to do this.')
        user = User.query.get_or_404(user_id_requested, description='User does not exist or has been deleted.')
        return user, 200

    @jwt_required(fresh=True)
    @use_kwargs(user_update_schema)
    @marshal_with(user_detail_schema)
    @doc(description='Update s user.')
    def patch(self, *args, **kwargs):
        user_id_requested = kwargs.get('user_id')

        user = User.query.get_or_404(user_id_requested, description='User does not exist or has been deleted.')

        if get_jwt_identity() != user.id:
            abort(403, message='You can\'t to edit this user.')

        json_data = request.get_json()
        for key, value in json_data.items():
            if key == 'password':
                value = generate_password_hash(value, method='sha256')
            if value:
                setattr(user, key, value)

        db.session.commit()
        return user, 200

    @jwt_required(fresh=True)
    @marshal_with(MessageResponseSchema)
    @doc(description='Delete a user.')
    def delete(self, *args, **kwargs):
        user = User.query.get_or_404(kwargs.get('user_id'), description='User does not exist or has been deleted.')

        if user.id != get_jwt_identity():
            abort(403, message='You don\'t have a permissions to delete this user.')

        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200



