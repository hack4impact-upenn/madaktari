from flask import flash, redirect, render_template, request, url_for
from flask_login import (current_user, login_required, login_user,
                         logout_user)
from flask_rq import get_queue
import json
from dateutil import parser
import logging

from . import account
from .. import db, csrf
from ..email import send_email
from ..models import User, Team, DateRange, Permission, Profile, TeamMember
from .forms import (ChangeEmailForm, ChangePasswordForm, CreatePasswordForm,
                    LoginForm, RegistrationForm, RequestResetPasswordForm,
                    ResetPasswordForm, ProfileForm)
from ..decorators import accepted_required

from .overlap import (all_interval_overlap)


@account.route('/')
@login_required
def index():
    """Account dashboard page."""
    return render_template('account/index.html', Permission=Permission)


@account.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.password_hash is not None and \
                user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('You are now logged in. Welcome back!', 'success')
            return redirect(request.args.get('next') or url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/login.html', form=form)


@account.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        confirm_link = url_for('account.confirm', token=token, _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='Confirm Your Account',
            template='account/email/confirm',
            user=user,
            confirm_link=confirm_link)
        flash('A confirmation link has been sent to {}.'.format(user.email),
              'warning')
        return redirect(url_for('main.index'))
    return render_template('account/register.html', form=form)


@account.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@account.route('/manage', methods=['GET', 'POST'])
@account.route('/manage/info', methods=['GET', 'POST'])
@login_required
def manage():
    """Display a user's account information."""
    return render_template('account/manage.html', user=current_user, form=None)


@account.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Respond to existing user's request to reset their password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = RequestResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_password_reset_token()
            reset_link = url_for(
                'account.reset_password', token=token, _external=True)
            get_queue().enqueue(
                send_email,
                recipient=user.email,
                subject='Reset Your Password',
                template='account/email/reset_password',
                user=user,
                reset_link=reset_link,
                next=request.args.get('next'))
        flash('A password reset link has been sent to {}.'
              .format(form.email.data), 'warning')
        return redirect(url_for('account.login'))
    return render_template('account/reset_password.html', form=form)


@account.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset an existing user's password."""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid email address.', 'form-error')
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.new_password.data):
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('account.login'))
        else:
            flash('The password reset link is invalid or has expired.',
                  'form-error')
            return redirect(url_for('main.index'))
    return render_template('account/reset_password.html', form=form)


@account.route('/manage/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change an existing user's password."""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.', 'form-success')
            return redirect(url_for('main.index'))
        else:
            flash('Original password is invalid.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    """Respond to existing user's request to change their email."""
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            change_email_link = url_for(
                'account.change_email', token=token, _external=True)
            get_queue().enqueue(
                send_email,
                recipient=new_email,
                subject='Confirm Your New Email',
                template='account/email/change_email',
                # current_user is a LocalProxy, we want the underlying user
                # object
                user=current_user._get_current_object(),
                change_email_link=change_email_link)
            flash('A confirmation link has been sent to {}.'.format(new_email),
                  'warning')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'form-error')
    return render_template('account/manage.html', form=form)


@account.route('/manage/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    """Change existing user's email with provided token."""
    if current_user.change_email(token):
        flash('Your email address has been updated.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.route('/confirm-account')
@login_required
def confirm_request():
    """Respond to new user's request to confirm their account."""
    token = current_user.generate_confirmation_token()
    confirm_link = url_for('account.confirm', token=token, _external=True)
    get_queue().enqueue(
        send_email,
        recipient=current_user.email,
        subject='Confirm Your Account',
        template='account/email/confirm',
        # current_user is a LocalProxy, we want the underlying user object
        user=current_user._get_current_object(),
        confirm_link=confirm_link)
    flash('A new confirmation link has been sent to {}.'.format(
        current_user.email), 'warning')
    return redirect(url_for('main.index'))


@account.route('/confirm-account/<token>')
@login_required
def confirm(token):
    """Confirm new user's account with provided token."""
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm_account(token):
        flash('Your account has been confirmed.', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@account.before_app_request
def before_request():
    """Force user to confirm email before accessing login-required routes."""
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:8] != 'account.' \
            and request.endpoint != 'static':
        return redirect(url_for('account.unconfirmed'))


@account.route('/unconfirmed')
def unconfirmed():
    """Catch users with unconfirmed emails."""
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('account/unconfirmed.html')


@account.route(
    '/join-from-invite/<int:user_id>/<token>', methods=['GET', 'POST'])
def join_from_invite(user_id, token):
    """
    Confirm new user's account with provided token and prompt them to set
    a password.
    """
    if current_user is not None and current_user.is_authenticated:
        flash('You are already logged in.', 'error')
        return redirect(url_for('main.index'))

    new_user = User.query.get(user_id)
    if new_user is None:
        return redirect(404)

    if new_user.password_hash is not None:
        flash('You have already joined.', 'error')
        return redirect(url_for('main.index'))

    if new_user.confirm_account(token):
        form = CreatePasswordForm()
        if form.validate_on_submit():
            new_user.password = form.password.data
            db.session.add(new_user)
            db.session.commit()
            flash('Your password has been set. After you log in, you can '
                  'go to the "Your Account" page to review your account '
                  'information and settings.', 'success')
            return redirect(url_for('account.login'))
        return render_template('account/join_invite.html', form=form)
    else:
        flash('The confirmation link is invalid or has expired. Another '
              'invite email with a new link has been sent to you.', 'error')
        token = new_user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=new_user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=new_user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=new_user,
            invite_link=invite_link)
    return redirect(url_for('main.index'))


@account.route('/edit_profile', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        prev_profiles = Profile.query.filter_by(user_id=current_user.id).all()
        for x in prev_profiles:
            db.session.delete(x)
        user = Profile(
            degrees=form.degrees.data,
            location=form.location.data,
            profile_pic=form.profile_pic.data,
            experience_abroad=form.experience_abroad.data,
            contact_email=form.email.data,
            contact_phone=form.phone.data,
            linkedin=form.linkedin.data,
            cv_link=form.cv_link.data,
            user_id=current_user.id)
        db.session.add(user)
        current_user.email = form.email.data
        db.session.commit()
        return redirect(url_for('account.edit_profile'))
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if profile:
        form.degrees.data = profile.degrees
        form.location.data = profile.location
        form.profile_pic.data = profile.profile_pic
        form.experience_abroad.data = profile.experience_abroad
        form.email.data = profile.contact_email
        form.phone.data = profile.contact_phone
        form.linkedin.data = profile.linkedin
        form.cv_link.data = profile.cv_link
    else:
        form.email.data = current_user.email
    return render_template('account/edit_profile.html', form=form)

@account.route('/view-profile/<int:id>', methods=['GET'])
@login_required
def view_profile(id):
    user = User.query.get(id)
    profile_obj = User.query.get(id).profile.first()
    return render_template('account/view_profile.html',user=user,  profile_obj=profile_obj)

@account.route('/edit_dates', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def edit_dates():
    if request.method == 'POST':
        ranges = request.json
        existing_ranges = current_user.date_ranges
        for r in existing_ranges:
            current_user.date_ranges.remove(r)
            db.session.delete(r)
        db.session.commit()
        for r in ranges:
            new_range = DateRange(start_date=parser.parse(r['start']), end_date=parser.parse(r['end']))
            print(new_range.start_date)
            db.session.add(new_range)
            current_user.date_ranges.append(new_range)
        db.session.commit()
        flash('Your selected date ranges have been saved.', 'success')
    return render_template('account/edit_dates.html', dateranges=current_user.date_ranges)


@account.route('/find_teammates', methods=['GET', 'POST'])
@login_required
def find_teammates():
    accepted_users = User.query.filter_by(role_id=3)
    # remove current user
    accepted_users = [u for u in accepted_users if u.id != current_user.id]
    teams = current_user.get_teams()
    return render_template('account/accepted_users.html', users=accepted_users, teams=teams)


@account.route('/team', methods=['GET', 'POST'])
@login_required
def see_team():
    teams = current_user.get_teams()
    print("teams: ")
    print(teams)
    teams = [x for x in teams if x is not None]
    return redirect(url_for('team.index', active='team'))


@account.route('/add_to_team', methods=['GET', 'POST'])
def add_to_team():
    user_id = request.args.get('user_id')
    team_id = request.args.get('team_id')
    new_team_name = request.args.get('new_team_name')

    if team_id == "new_team":
        team = Team(current_user, new_team_name)
        db.session.add(team)
        db.session.commit()
    else:
        team = Team.query.get(team_id)

    user = User.query.get(user_id)
    str = 'The person is already  a member of {}!'.format(team.team_name)
    if int(user_id) not in [int(x.user_id) for x in team.team_members]:
        team.add_to_team(user)
        db.session.add(team)
        db.session.commit()
        str = 'This person was successfully added to team {}'.format(team.team_name)
    flash(str, 'info')
    return redirect(url_for('account.see_team'))


@account.route('/team/<int:team_id>')
@account.route('/team/<int:team_id>/info')
@login_required
def team_info(team_id):
    """View a team's profile."""
    team = Team.query.filter_by(id=team_id).first()
    if team is None:
        pass
    return render_template('admin/manage_team.html', team=team)


@account.route('/team/<int:team_id>/remove-member/<int:user_id>', methods=['GET', 'POST'])
@login_required
def remove_member(team_id, user_id):
    """Change a team's email."""
    team = Team.query.filter_by(id=team_id).first()
    l = [x for x in team.team_members if x.user_id == user_id]
    if len(l) > 0:
        tm = TeamMember.query.get(l[0].id)
        db.session.delete(tm)
        db.session.commit()
    flash('{} was succesfully deleted'
          .format(User.query.get(user_id).last_name , 'form-success'))
    return redirect(url_for('team.index', active='team'))

@account.route('/team/<int:team_id>/make-owner/<int:user_id>', methods=['GET', 'POST'])
@login_required
def make_owner(team_id, user_id):
    """Change a team's email."""
    team = Team.query.filter_by(id=team_id).first()
    l = team.team_members
    for t in l:
        if t.user_id == user_id:
            t.is_owner = True
        else:
            t.is_owner = False
        db.session.add(t)
        db.session.commit()
    flash('{} was succesfully made an owner'
          .format(User.query.get(user_id).last_name , 'form-success'))
    return redirect(url_for('account.see_team'))


@account.route('/useroverlaps', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def useroverlaps():
    users = User.query.all()
    all_user_overlap = []
    for user in users:
        print(user.first_name)
        overlap_list = all_interval_overlap(current_user.date_ranges, user.date_ranges)
        currMax = 0
        overlap = []
        for date in overlap_list:
            print(user.first_name)
            print(date)
            diff = date['end'] - date['start']
            if diff.total_seconds() > currMax:
                currMax = diff
                overlap = date
        all_user_overlap.append({'user' : user, 'overlap' : overlap})

    return render_template('account/useroverlaps.html', ranges=all_user_overlap)



