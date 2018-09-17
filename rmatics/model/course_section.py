from rmatics.model import db
from rmatics.utils.functions import attrs_to_dict

from rmatics.model.course_module import CourseModuleInstance

class CourseSection(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_course_sections'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column('course', db.Integer, db.ForeignKey('moodle.mdl_course.id'))
    section = db.Column(db.Integer)
    summary = db.Column(db.Text)
    sequence_text = db.Column('sequence', db.Text)
    visible = db.Column(db.Boolean)

    course = db.relationship('Course', backref=db.backref('sections', lazy='dynamic', order_by='CourseSection.section'))

    @property
    def sequence(self):
        if not hasattr(self, '_sequence'):
            try:
                self._sequence = list(map(int, self.sequence_text.split(',')))
            except Exception:
                self._sequence = []
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        self._sequence = value
        self.sequence_text = ','.join(list(map(str, value)))

    def serialize(self):
        serialized = attrs_to_dict(
            self,
            'id',
            'course_id',
            'section',
            'summary',
            'sequence',
            'visible',
        )
        serialized['modules'] = [
            module.serialize()
            for module in self.modules.filter_by(visible=True).all()
        ]

        return serialized
