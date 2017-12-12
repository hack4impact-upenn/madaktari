from flask import url_for
from flask_login import current_user
from flask_wtf import Form
from wtforms import ValidationError
from wtforms.fields import (BooleanField, PasswordField, StringField,
                            SubmitField, HiddenField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length, URL
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
import phonenumbers
from ..models import User
from .. import db


class LoginForm(Form):
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    first_name = StringField(
        'First name', validators=[InputRequired(), Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(), EqualTo('password2', 'Passwords must match')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. (Did you mean to '
                                  '<a href="{}">log in</a> instead?)'
                                  .format(url_for('account.login')))

class ProfileForm(Form):
    degrees = StringField(
        'Degrees', validators=[InputRequired(), Length(1, 64)])
    location = StringField(
        'Location', validators=[InputRequired(), Length(1, 64)])
    experience_abroad = StringField(
        'Previous Experience Abroad', validators=[InputRequired(), Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    phone = StringField('Phone', validators=[InputRequired(), Length(1, 15)])
    linkedin = StringField(
        'LinkedIn', validators=[Length(1, 64), URL()])
    cv_link = StringField(
        'Link to CV', validators=[Length(1, 64), URL()])
    profile_pic = HiddenField(
        '')
    submit = SubmitField('Submit')
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        print(field.data)
        print(user)
        if (user is not None) and user.id != current_user.id:
            raise ValidationError('Email already registered.')
    def validate_phone(self, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number (longer than 16 characters)')
        try:
            number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(number)):
                raise ValidationError('Invalid phone number')
        except:
            number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(number)):
                raise ValidationError('Invalid phone number')

class RequestResetPasswordForm(Form):
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    submit = SubmitField('Reset password')

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(Form):
    email = EmailField(
        'Email', validators=[InputRequired(), Length(1, 64), Email()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(), EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(Form):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(), EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Set password')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[InputRequired()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(), EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Update password')


class ChangeEmailForm(Form):
    email = EmailField(
        'New email', validators=[InputRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
