from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length

from ..models import User


class ReferCandidateForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Invite')

    @staticmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
