from flask import render_template, url_for, flash
from flask_login import current_user, login_required
from flask_rq import get_queue
from ..models import EditableHTML, User

from . import main


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


