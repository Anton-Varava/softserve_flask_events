from app import db


class User(db.Model):
    """
        description: User description
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    is_superuser = db.Column(db.Boolean, default=False)
    events = db.relationship('Event', backref=db.backref('organizer', lazy='joined'), lazy='dynamic')
    participant_events = db.relationship('EventParticipant', backref=db.backref('participant_events',
                                                                                lazy='joined'), lazy='dynamic')

    def __repr__(self):
        return f'<User {self.first_name}, {self.email}>'
