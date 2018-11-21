from rmatics.model.base import db


class UserOAuthProvider(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'user_oauth_provider'

    user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'), primary_key=True)
    provider = db.Column(db.String(255), primary_key=True)
    oauth_id = db.Column(db.String(255))

    user = db.relationship('SimpleUser', backref=db.backref('oauth_ids', lazy='dynamic'))
