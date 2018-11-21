from rmatics.model.base import db
from rmatics.model.course_module import CourseModuleInstance
from rmatics.utils.functions import attrs_to_dict


class Monitor(CourseModuleInstance, db.Model):
    """
    Модуль курса, описывающий монитор
    """
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_monitor'
    __mapper_args__ = {
        'polymorphic_identity': 'monitor',
        'concrete': True,
    }

    MODULE = 28

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column('course', db.Integer)
    name = db.Column(db.Unicode(255))

    @staticmethod
    def url(course_module_id):
        return f'http://informatics.msk.ru/mod/monitor/view.php?id={course_module_id}'

    def serialize(self, course_module_id=None):
        serialized = attrs_to_dict(
            self,
            'id',
            'course_id',
            'name',
        )
        if course_module_id:
            serialized['url'] = Monitor.url(course_module_id)
        return serialized
