from .. import db, login_manager


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    # owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    members = db.relationship('TeamMember', backref='team')
    is_confirmed = db.Column(db.Boolean)


class TeamMember(db.Model):
    __tablename = 'teammember'
    id = db.Column(db.Integer, primary_key=True)
    is_confirmed = db.Boolean
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('teammember', uselist=False))