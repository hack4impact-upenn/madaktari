from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from flask_rq import get_queue
from . import team
from .. import db
from ..models import User, Team, Role
from ..email import send_email

from .forms import ReferCandidateForm


@team.route('/',  methods=['GET', 'POST'])
@login_required
def index():
    """ Primary Page for Teams View """
    accepted_role = Role.query.filter_by(name='Accepted').first()
    accepted_users = db.session.query(User).filter(User.role == accepted_role
                                                   and User.id != current_user.id)  # remove current user
    teams = current_user.get_teams()
    referral_form = ReferCandidateForm()
    if referral_form.validate_on_submit():
        applicant_role = Role.query.filter_by(name='Applicant').first()
        user = User(
            role=applicant_role,
            first_name=referral_form.first_name.data,
            last_name=referral_form.last_name.data,
            email=referral_form.email.data)
        current_user.candidates.append(user)
        user.referrers.append(current_user)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link, )
        flash('Candidate {} successfully referred'.format(user.full_name()),
              'form-success')
    return render_template('team/index.html', users=accepted_users, teams=teams, User=User, form=referral_form)


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

    return redirect(url_for('team.index'))



