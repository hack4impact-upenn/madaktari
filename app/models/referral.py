from .. import db


class Referral(db.Model):
    __tablename__ = 'referrals'
    id = db.Column(db.Integer, primary_key=True)
    referrer = db.Column(db.String(64)) #TODO: Refer to the user object
    candidate = db.Column(db.String(64)) #TODO: update to user object when they sign up
