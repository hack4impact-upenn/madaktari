from .. import db


class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.PickleType, unique=False)

    @staticmethod
    def get_form_content():
        return Form.query.order_by('id desc').first()
