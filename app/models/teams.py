from .. import db, login_manager


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    team_members = db.relationship('TeamMember')
    is_confirmed = db.Column(db.Boolean)

    def __init__(self, user):
        new_team_member = TeamMember(is_confirmed=False, is_owner=True)
        user.team_memberships.append(new_team_member)
        self.team_members.append(new_team_member)
        self.is_confirmed = False

    def add_to_team(self, user):
        new_team_member = TeamMember(is_confirmed=False, is_owner=False)
        user.team_memberships.append(new_team_member)
        self.team_members.append(new_team_member)
        self.is_confirmed = False

    def get_owner(self):
        for team_member in self.team_members:
            if team_member.is_owner:
                return team_member


class TeamMember(db.Model):
    __tablename = 'TeamMember'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_confirmed = db.Column(db.Boolean)
    is_owner = db.Column(db.Boolean)

