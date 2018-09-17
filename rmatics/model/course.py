from collections import OrderedDict

from rmatics.model import db
from rmatics.utils.functions import attrs_to_dict


class Course(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_course'

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column('fullname', db.Unicode(254))
    short_name = db.Column('shortname', db.Unicode(100))

    category = db.Column(db.Integer)
    password = db.Column(db.Unicode(50))
    visible = db.Column(db.Boolean)

    def require_password(self):
        return bool(self.password)

    def serialize(self):
        serialized = attrs_to_dict(
            self,
            'id',
            'full_name',
            'short_name',
        )
        serialized['require_password'] = self.require_password()

        if not self.require_password():
            serialized['sections'] = [
                section.serialize()
                for section in self.sections.all()
                if section.visible
            ]
        return serialized
