from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, InputRequired, Length


class ReferCandidateForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Invite')
