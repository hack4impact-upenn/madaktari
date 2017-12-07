from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import team
from .. import db
from ..models import User, Team, Role


@team.route('/')
@login_required
def index():
    """ TODO: Teams primary page"""
    accepted_role = Role.query.filter_by(name='Accepted').first()
    accepted_users = db.session.query(User).filter(User.role == accepted_role
                                                   and User.id != current_user.id)  # remove current user
    teams = current_user.get_teams()
    return render_template('account/accepted_users.html', users=accepted_users, teams=teams, User=User)


@team.route('/add_to_team', methods=['GET', 'POST'])
def add_to_team():
    user_id = request.args.get('user_id')
    team_id = request.args.get('team_id')
    new_team_name = request.args.get('new_team_name')

    if team_id == "new_team":
        target_team = Team(current_user, new_team_name)
        db.session.add(team)
        db.session.commit()
    else:
        target_team = Team.query.get(team_id)

    user = User.query.get(user_id)
    target_team.add_to_team(user)

    return redirect(url_for('team.index'));

