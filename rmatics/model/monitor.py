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
    name = db.Column(db.Unicode(255), nullable=False, default='')
    monitor_id = db.Column(db.Integer, nullable=False, default=0)
    group_id = db.Column(db.Integer, nullable=False, default=0)

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


class MonitorStatement(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_monitors_statements'

    id = db.Column(db.Integer, primary_key=True)
    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    monitor_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_monitors_statements.id'))
