from .. import db
from . import User

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)

    @staticmethod
    def get_form_content():
        return Form.query.order_by('id desc').first().content

class FormResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    def __init__(self, user_id, content):
        self.content = content
        self.user_id = user_id
