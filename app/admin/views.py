from flask import abort, flash, redirect, render_template, url_for, request, \
                  jsonify
from flask_login import current_user, login_required
from flask_rq import get_queue

from .forms import (ChangeAccountTypeForm, ChangeUserEmailForm, InviteUserForm,
                    NewUserForm)
from . import admin
from .. import db, csrf
from ..decorators import admin_required
from ..email import send_email
from ..models import Role, User, EditableHTML, Form, FormResponse
import json
import jsonpickle


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
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
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'
              .format(user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'
              .format(user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def disable_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def disable_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        user.role = Role.query.filter_by(name='Applicant').first()
        db.session.add(user)
        db.session.commit()
        flash('Successfully disabled user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/create-form', methods=['GET', 'POST'])
@login_required
@admin_required
def create_form_index():
    form = {}
    try:
        f = Form.get_form_content()
        if f is not None:
            print(f)
            form = json.dumps(jsonpickle.decode(f))
    except Exception as e:
        print(e)
        form = {}
    return render_template('admin/create_form.html', form=form)


@admin.route('/update-form', methods=['POST'])
@csrf.exempt
def update_form():
    content = jsonpickle.encode(json.loads(request.json))
    form = Form(content=content)
    db.session.add(form)
    db.session.commit()
    return jsonify({'status': 200})


@admin.route('/view-responses', methods=['GET'])
@login_required
@admin_required
def get_responses():
    responses = db.session.query(FormResponse.id).join(FormResponse.user_id).group_by(FormResponse.user_id)
    responses = [r for r in responses if r.user.is_role('Pending')]
    return render_template('admin/view_responses.html', responses=responses)


@admin.route('/view-response/<int:user_id>', methods=['GET','POST'])
@login_required
@admin_required
def get_response(user_id):
    r = FormResponse.query.filter_by(user_id=user_id).order_by('id desc').first()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form_resp_obj = []
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
                if x['name'] == k_new:
                    form_resp_obj.append({'idx': idx, 'label': x['label'], 'resp': form_resp[k]})
        form_resp_obj = sorted(form_resp_obj, key=lambda k: k['idx'])
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('User status {} successfully changed to {}.'
              .format(user.full_name(), user.role.name), 'form-success')
    return render_template('admin/form_response.html', form_resp_obj=form_resp_obj, user=user, form=form)
