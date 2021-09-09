from app import app, db
from models.user import User
from schemas.user import user_schema, user_list_schema
from flask_restful import Resource, abort, reqparse
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash


class UserAPIView(Resource):
    def post(self):
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = User(first_name=data.get('first_name'),
                        second_name=data.get('second_name'),
                        email=data.get('email'),
                        password=hashed_password)


        db.session.add(new_user)
        db.session.commit()

        return user_schema.dump(new_user), 201

    def get(self):
        users = User.query.all()
        return user_list_schema.dump(users), 200


class UserDetailAPIView(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            abort(404, message='User does not exist or has been deleted.')
        return user_schema.dump(user), 200

    def patch(self, user_id):
        user = User.query.get(user_id)
        if not user:
            abort(404, message='User does not exist or has been deleted.')

        json_data = request.get_json()
        for key, value in json_data.items():
            if value:
                setattr(user, key, value)

        db.session.commit()
        return user_schema.dump(user), 200

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            abort(404, message='User does not exist or has been deleted.')
        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted successfully'}, 200
