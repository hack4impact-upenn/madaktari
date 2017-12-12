from .. import db

class Profile(db.Model):
    __tablename__ = "profiles"
    id = db.Column(db.Integer, primary_key=True)
    degrees = db.Column(db.String(128))
    location = db.Column(db.String(128))
    experience_abroad = db.Column(db.String(128))
    contact_email = db.Column(db.String(64), unique=True)
    contact_phone = db.Column(db.String(15), unique=True)
    linkedin = db.Column(db.String(64))
    cv_link = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
