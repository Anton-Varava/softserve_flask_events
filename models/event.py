from app import db

class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status_code = db.Column(db.SmallInteger, db.ForeignKey('event_statuses.code'), nullable=True)
    description = db.Column(db.String(5000), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Event:{self.id}. {self.title} at {self.date}. Status - {self.status_code}'





