from .. import db, login_manager


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    members = db.relationship('User', db.backref('team'))
    is_confirmed = db.Column(db.Boolean)
