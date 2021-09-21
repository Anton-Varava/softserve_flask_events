from app import ma
from models.event_status import EventStatus


class EventStatusSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EventStatus
        load_instance = True
        include_fk = True
        fields = ('code', 'title')


event_status_schema = EventStatusSchema()
event_list_status_schema = EventStatusSchema(many=True)
