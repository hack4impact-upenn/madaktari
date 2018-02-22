from flask import flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required

from flask_rq import get_queue
from . import team
from .. import db, csrf
from ..models import User, Team, Role, FeedbackForm, FeedbackFormResponse
from ..email import send_email

from .forms import ReferCandidateForm
from ..account.overlap import (all_interval_overlap)
import jsonpickle


@team.route('/',  methods=['GET', 'POST'])
@team.route('/<string:active>',  methods=['GET', 'POST'])
@login_required
def index(active=''):
    if active is '':
        active = 'create'
    """ Primary Page for Teams View """
    accepted_role = Role.query.filter_by(name='Accepted').first()
    accepted_users = db.session.query(User).filter(User.role == accepted_role
                                                   and User.id != current_user.id)  # remove current user
    teams = current_user.get_teams()
    teams = [x for x in teams if x is not None]

    overlapping_dates = {}
    users = User.query.all()
    for user in users:
        overlap_list = all_interval_overlap(current_user.date_ranges, user.date_ranges)
        currMax = 0
        overlap = []
        for date in overlap_list:
            diff = date['end'] - date['start']
            if diff.total_seconds() > currMax:
                currMax = diff.total_seconds()
                overlap = date
        overlapping_dates[user.id] = overlap
    print(overlapping_dates)


    referral_form = ReferCandidateForm()
    if referral_form.validate_on_submit():
        applicant_role = Role.query.filter_by(name='Applicant').first()
        if User.query.filter_by(email=referral_form.email.data).count() == 0:
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
        active='refer'
    
    return render_template('team/index.html', users=accepted_users, teams=teams, User=User, form=referral_form, active=active, overlapping_dates=overlapping_dates)


@team.route('/add_to_team', methods=['GET', 'POST'])
def add_to_team():
    user_id = request.args.get('user_id')
    team_id = request.args.get('team_id')
    new_team_name = request.args.get('new_team_name')

    if team_id == "new_team":
        target_team = Team(current_user, new_team_name)
        db.session.add(target_team)
        db.session.commit()
    else:
        target_team = Team.query.get(team_id)

    user = User.query.get(int(user_id))
    target_team.add_to_team(user)

    return redirect(url_for('team.index', active='team'))


@team.route('/feedback')
@login_required
def form():
    content = None
    form_resp_obj = []
    try:
        content = FeedbackForm.get_form_content()
        if current_user.is_authenticated:
            r = FeedbackFormResponse.query.filter_by(user_id=current_user.id).order_by('id desc').first()
            raw_form_content = ''
            if r.form:
                raw_form_content = r.form.content
            raw_form_resp = r.content
            if raw_form_content and raw_form_resp:
                form_content = jsonpickle.decode(raw_form_content)
                form_resp = jsonpickle.decode(raw_form_resp)
                for k in form_resp:
                    k_new = k.replace('[]', '')
                    for idx, x in enumerate(form_content):
                        try:
                            if x['name'] == k_new:
                                form_resp_obj.append({'idx': idx, 'label': x['label'], 'resp': form_resp[k]})
                        except:
                            pass
                form_resp_obj = sorted(form_resp_obj, key=lambda k: k['idx'])
        print(content)
        return render_template('team/feedback_form.html', content=content, form_resp_obj=form_resp_obj)
    except Exception:
        return render_template('team/feedback_form.html', content=content, form_resp_obj=form_resp_obj)
        pass

@team.route('/submit-form', methods=['POST'])
@csrf.exempt
def submit_form():
    print(request.json)
    content = jsonpickle.encode(request.json)
    print(content)
    current_form = FeedbackForm.query.order_by('id desc').first()
    form = FeedbackFormResponse(user_id=current_user.id, content=content,
                        form_id=current_form.id)
    db.session.add(form)
    db.session.commit()
    return jsonify({'status': 200})
