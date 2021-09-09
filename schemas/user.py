from app import ma
from models.user import User


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = ma.auto_field()
    first_name = ma.auto_field()
    second_name = ma.auto_field()
    email = ma.auto_field()


user_schema = UserSchema()
user_list_schema = UserSchema(many=True)