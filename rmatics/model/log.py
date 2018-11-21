from sqlalchemy.sql import func

from rmatics.model.base import db


class Log(db.Model):
    """
    Модель лога действия пользователя.
    """
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'))
    instance_id = db.Column(db.Integer)
    action_id = db.Column(db.Integer, db.ForeignKey('pynformatics.action.id'))

    created_at = db.Column(db.DateTime, default=func.now())

    action = db.relationship('Action', backref=db.backref('logs', lazy='select'), lazy='joined')
    user = db.relationship('SimpleUser', backref=db.backref('logs', lazy='select'), lazy='joined')
