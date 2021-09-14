from app import db


class ParticipantStatus(db.Model):
    __tablename__ = 'participant_statuses'

    code = db.Column(db.SmallInteger, primary_key=True)
    title = db.Column(db.String(50))
    events = db.relationship('EventParticipant', backref=db.backref('participant_status', lazy='joined'), lazy='dynamic')

    def __repr__(self):
        return f'<Status {self.code}, {self.title}>'
