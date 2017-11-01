from flask import render_template, request
from flask_login import current_user
import wtforms
import json
import jsonpickle

from ..models import EditableHTML, Form, FormResponse
from .. import csrf
from . import main

import logging


@main.route('/')
def index():
    content = None
    try:
        content = Form.get_form_content()
    except Exception:
        pass
    return render_template('main/index.html', content=content)

@main.route('/submit-form', methods=['POST'])
@csrf.exempt
def submit_form():
    content = jsonpickle.encode(request.json)
    form = FormResponse(user_id=current_user.id, content=content)
    db.session.add(form)
    db.session.commit()
    return jsonify({'status': 200})

@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)
