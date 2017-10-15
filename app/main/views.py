from flask import render_template, url_for, flash
from flask_login import current_user, login_required
from flask_rq import get_queue
from ..models import EditableHTML, User, Referral

from . import main
from .forms import ReferUserForm
from .. import db
from ..email import send_email


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template('main/about.html',
                           editable_html_obj=editable_html_obj)


@main.route('/referral', methods=['GET', 'POST'])
<<<<<<< HEAD
=======
@login_required
>>>>>>> 0559affa7d40eb9e8b95f73680cb4495bc71b01f
def refer_user():
    """Invites a new user to create an account and set their own password."""
    form = ReferUserForm()
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        referral_record = Referral(
                referrer=current_user.full_name(),
                candidate=user.full_name()
                )
        db.session.add(user)
        db.session.add(referral_record)
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
    return render_template('main/referral.html', form=form)

