from flask import flash, render_template, request, jsonify, abort, url_for, redirect
from flask_rq import get_queue
from flask_login import current_user, login_user

import os, time, json
import boto3

import jsonpickle
import os
import boto3
import time
import json
from .. import db, csrf
from ..models import EditableHTML, Form, FormResponse, Role, User
from ..email import send_email
from . import main
from .forms import LoginForm, RegistrationForm


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        if current_user.is_role('Applicant'):
            print('hi')
            return redirect(url_for('main.form'))

        elif current_user.is_role('Pending'):
            print('h2i')
            return redirect(url_for('main.form'))

        elif current_user.is_role('Accepted'):
            print('h3i')
            return redirect(url_for('account.index'))

        elif current_user.is_role('Rejected'):
            print('h4i')
            return redirect(url_for('account.index'))

        elif current_user.is_role('Administrator'):
            print('h5i')
            return redirect(url_for('admin.index'))

    return redirect(url_for('main.register'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user, and send them a confirmation email."""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            confirmed=True,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        confirm_link = url_for('account.confirm', token=token, _external=True)
        # get_queue().enqueue(
            # send_email,
            # recipient=user.email,
            # subject='Confirm Your Account',
            # template='account/email/confirm',
            # user=user,
            # confirm_link=confirm_link)
        flash('Account successfully created',
              'success')
        return redirect(url_for('main.index'))
    return render_template('main/register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
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
    return render_template('main/login.html', form=form)


@main.route('/form')
def form():
    content = None
    form_resp_obj = []
    try:
        content = Form.get_form_content()
        if current_user.is_authenticated and current_user.is_role('Pending'):
            r = FormResponse.query.filter_by(user_id=current_user.id).order_by('id desc').first()
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
    except Exception:
        pass
    return render_template('main/form.html', content=content, form_resp_obj=form_resp_obj)


@main.route('/edit-form')
def edit_form():
    user = User.query.filter_by(id=current_user.id).first()
    if user is None:
        abort(403)
    user.role = Role.query.filter_by(name='Applicant').first()
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route('/submit-form', methods=['POST'])
@csrf.exempt
def submit_form():
    print(request.json)
    content = jsonpickle.encode(request.json)
    print(content)
    current_form = Form.query.order_by('id desc').first()
    form = FormResponse(user_id=current_user.id, content=content,
                        form_id=current_form.id)
    user=User.query.filter_by(id=current_user.id).first()
    if user is None:
        abort(404)
    user.role = Role.query.filter_by(name='Pending').first()
    db.session.add(user)
    db.session.add(form)
    db.session.commit()
    return jsonify({'status': 200})


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)

@main.route('/sign-s3/')
def sign_s3():
    # Load necessary information into the application
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_REGION = os.environ.get('S3_REGION')
    TARGET_FOLDER = 'json/'
    # Load required data from the request
    pre_file_name = request.args.get('file-name') 
    file_name = ''.join(pre_file_name.split('.')[:-1]) + str(time.time()).replace('.','-') + '.' + ''.join(pre_file_name.split('.')[-1:])
    file_type = request.args.get('file-type')

  # Initialise the S3 client
    s3 = boto3.client('s3', 'us-west-2')

    # Generate and return the presigned URL
    presigned_post = s3.generate_presigned_post(
            Bucket = S3_BUCKET,
            Key = TARGET_FOLDER + file_name,
            Fields = {"acl": "public-read", "Content-Type": file_type},
            Conditions = [
                {"acl": "public-read"},
                {"Content-Type": file_type}
                ],
            ExpiresIn = 6000
            )

    # Return the data to the client
    return json.dumps({
        'data': presigned_post,
        'url_upload': 'https://%s.%s.amazonaws.com' % (S3_BUCKET, S3_REGION),
        'url': 'https://%s.amazonaws.com/%s/json/%s' % (S3_REGION, S3_BUCKET, file_name)
        })
