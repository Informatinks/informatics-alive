from rmatics.model import db
from rmatics.model.course_module import CourseModuleInstance
from rmatics.utils.functions import attrs_to_dict


class Label(CourseModuleInstance, db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_label'
    __mapper_args__ = {
        'polymorphic_identity': 'label',
        'concrete': True,
    }

    MODULE = 9

    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.Integer)
    name = db.Column(db.Unicode(255))
    content = db.Column(db.UnicodeText)

    def serialize(self):
        return attrs_to_dict(
            self,
            'id',
            'name',
            'content',
        )
