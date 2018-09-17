import time

from rmatics.model import db
from rmatics.utils.functions import attrs_to_dict


class Participant(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_virtualcontest'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'))
    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    start = db.Column(db.Integer)
    duration =db. Column(db.Integer)

    user = db.relationship('SimpleUser', backref=db.backref('pariticipants', lazy='dynamic'))
    statement = db.relationship('Statement', backref=db.backref('participants', lazy='dynamic'))

    def finished(self):
        return time.time() >= self.start + self.duration

    def serialize(self):
        return attrs_to_dict(
            self,
            'start',
            'duration',
            'statement_id',
        )
