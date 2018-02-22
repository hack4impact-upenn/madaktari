from .. import db


class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)
    responses = db.relationship('FormResponse', backref='form')

    @staticmethod
    def get_form_content():
        return Form.query.order_by('id desc').first().content



class FormResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))

class FeedbackForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)
    responses = db.relationship('FeedbackFormResponse', backref='form')

    @staticmethod
    def get_form_content():
        return FeedbackForm.query.order_by('id desc').first().content


class FeedbackFormResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    form_id = db.Column(db.Integer, db.ForeignKey('feedback_form.id'))
