from flask_restful import Resource, abort, reqparse

from flask_jwt_extended import jwt_required, get_jwt_identity

from marshmallow import ValidationError

from app import db
from models.event_status import EventStatus
from models.user import User
from schemas.event_status import event_status_schema, event_list_status_schema


event_status_args = reqparse.RequestParser()
event_status_args.add_argument('code', type=int, help='Code of the event status is required.', required=True)
event_status_args.add_argument('title', type=str, help='Title of the event status is required.', required=True)


class EventStatusAPIView(Resource):
    @jwt_required()
    def get(self, *args, **kwargs):
        event_statuses = EventStatus.query.all()
        return event_list_status_schema.dump(event_statuses)

    @jwt_required()
    def post(self, *args, **kwargs):
        current_user = User.query.get_or_404(get_jwt_identity())
        if not current_user.is_superuser:
            abort(403, message='You don\'t have a permissions to do this.')

        json_data = event_status_args.parse_args()
        try:
            data = event_status_schema.load(json_data)
        except ValidationError as err:
            return err.messages, 409

        new_status = EventStatus(code=data.get('code'), title=data.get('title'))
        db.session.add(new_status)
        db.session.commit()

        return event_status_schema.dump(new_status), 201

