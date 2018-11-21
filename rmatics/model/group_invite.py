from rmatics.model.base import db

from rmatics.utils.exceptions import GroupNotFound
from rmatics.utils.functions import attrs_to_dict
from rmatics.utils.url_encoder import (
    decode,
    encode,
)


class GroupInvite(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'group_invite'

    REDIRECT_COURSE = 'COURSE'
    REDIRECT_STATEMENT = 'STATEMENT'
    REDIRECT_TYPES = [
        REDIRECT_COURSE,
        REDIRECT_STATEMENT,
    ]

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_ejudge_group.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_user.id'))
    redirect_type = db.Column(db.Enum(*REDIRECT_TYPES))
    instance_id = db.Column(db.Integer)
    disabled = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False)

    group = db.relationship('Group', backref='group_invites', lazy='joined')
    creator = db.relationship('SimpleUser', backref='group_invites', lazy='joined')

    @property
    def redirect(self):
        if self.redirect_type == GroupInvite.REDIRECT_COURSE:
            return {'course_id': self.instance_id}
        elif self.redirect_type == GroupInvite.REDIRECT_STATEMENT:
            return {'statement_id': self.instance_id}
        else:
            raise NotImplementedError

    @property
    def url(self):
        return encode(self.id)

    @staticmethod
    def get_by_url(url):
        try:
            id = decode(url)
        except Exception:
            raise GroupNotFound

        group = db.session.query(GroupInvite).filter_by(id=id).first()
        if not group:
            raise GroupNotFound
        return group

    def serialize(self, attributes=None):
        if attributes is None:
            attributes = (
                'group_id',
                'creator_id',
                'redirect',
                'disabled',
                'url'
            )
        serialized = attrs_to_dict(self, *attributes)
        return serialized
