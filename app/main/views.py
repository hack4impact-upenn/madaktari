from flask import render_template, request, jsonify, abort, url_for, redirect

import os, time, json
import boto3

import jsonpickle
from ..models import EditableHTML, Form, FormResponse, Role, User
from .. import db, csrf
from . import main
from flask_login import current_user


@main.route('/')
def index():
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
    return render_template('main/index.html', content=content, form_resp_obj=form_resp_obj)


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
