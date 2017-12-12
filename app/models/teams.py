from .. import db, login_manager


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(64), index=True)
    team_members = db.relationship('TeamMember', backref="team")
    team_todos = db.relationship('TeamTodo', backref="team")
    is_confirmed = db.Column(db.Boolean)

    def __init__(self, user, team_name):
        new_team_member = TeamMember(is_confirmed=False, is_owner=True)
        user.team_memberships.append(new_team_member)
        self.team_members.append(new_team_member)
        print(self.team_members)
        self.is_confirmed = False
        self.team_name = team_name
        print(self.team_members)

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
    __tablename__ = 'TeamMember'
    id = db.Column(db.Integer, primary_key=True)
    is_confirmed = db.Column(db.Boolean)
    is_owner = db.Column(db.Boolean)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class TeamTodo(db.Model):
    __tablename__ = 'TeamTodos'
    id = db.Column(db.Integer, primary_key=True)
    is_done = db.Column(db.Boolean)
    content = db.Column(db.Text)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    description = db.Column(db.String(1000))
