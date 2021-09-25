from app import ma
from models.user import User
from marshmallow import fields


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = fields.Int(dump_only=True)
    first_name = fields.Str()
    second_name = fields.Str()
    email = fields.Email()
    password = fields.Str()


user_detail_schema = UserSchema(exclude=['password'])
user_create_schema = UserSchema(only=('email', 'password', 'first_name'))
user_login_schema = UserSchema(only=('email', 'password'))
user_update_schema = UserSchema()


class TokenSchema(ma.Schema):
    access_token = fields.Str()
    refresh_token = fields.Str()
    email = fields.Email()


login_token_schema = TokenSchema()
refresh_login_schema = TokenSchema(only=('access_token',))
