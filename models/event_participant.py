from app import db


class EventParticipant(db.Model):
    __tablename__ = 'event_participants'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status_code = db.Column(db.Integer, db.ForeignKey('participant_statuses.code'), default=10)
    status = db.relationship('ParticipantStatus', lazy=True)

    __table_args__ = (db.UniqueConstraint('event_id', 'user_id'),)

    def __repr__(self):
        return f'<Participant {self.user_id} on event {self.event_id}>'
