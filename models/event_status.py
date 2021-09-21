from app import db


class EventStatus(db.Model):
    __tablename__ = 'event_statuses'

    code = db.Column(db.SmallInteger, primary_key=True)
    title = db.Column(db.String(20))
    events = db.relationship('Event', backref=db.backref('event_status', lazy='joined'), lazy='select')

    def __repr__(self):
        return f'<Status {self.code}, {self.title}>'
