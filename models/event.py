from app import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status_code = db.Column(db.SmallInteger, db.ForeignKey('event_statuses.code'), nullable=True, default=10)
    description = db.Column(db.String(5000), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    participants = db.relationship('EventParticipant', backref=db.backref('event_participants'), lazy='dynamic')


    def __repr__(self):
        return f'<Event:{self.id}. {self.title} at {self.date}. Status - {self.status_code}'

    @property
    def is_current(self):
        return self.status_code == 20
