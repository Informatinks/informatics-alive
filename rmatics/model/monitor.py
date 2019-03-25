from rmatics.model.base import db
from rmatics.model.course_module import CourseModuleInstance


class MonitorCourseModule(CourseModuleInstance, db.Model):
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
    monitor_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_monitors.id'))
    group_id = db.Column(db.Integer, nullable=False, default=0)


class Monitor(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_monitors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer)
    type = db.Column(db.String(20))
    # Показывать ли участников без посылок
    show_empty = db.Column(db.Integer, default=0)


class MonitorStatement(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_monitors_statements'

    id = db.Column(db.Integer, primary_key=True)
    statement_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_statements.id'))
    monitor_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_monitors.id'))
    sort = db.Column(db.Integer)
