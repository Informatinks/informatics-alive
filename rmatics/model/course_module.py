from typing import Type

from sqlalchemy.ext.declarative import (
    AbstractConcreteBase,
    declared_attr
)

from rmatics.model.base import db
from rmatics.utils.decorators import deprecated
from rmatics.utils.functions import attrs_to_dict


class CourseModule(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_course_modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column('course', db.Integer, db.ForeignKey('moodle.mdl_course.id'))
    module = db.Column(db.Integer)
    instance_id = db.Column('instance', db.Integer)
    section_id = db.Column('section', db.Integer, db.ForeignKey('moodle.mdl_course_sections.id'))
    visible = db.Column(db.Boolean)

    course = db.relationship('Course', backref=db.backref('course_modules', lazy='dynamic'))
    section = db.relationship('CourseSection', backref=db.backref('modules', lazy='dynamic'))

    @property
    def instance(self) -> Type['CourseModuleInstance']:
        if not hasattr(self, '_instance'):
            instance_class = next(
                (
                    subclass
                    for subclass in CourseModuleInstance.__subclasses__()
                    if subclass.MODULE == self.module
                ),
                None
            )
            if not instance_class:
                self._instance = None
            else:
                self._instance = db.session.query(instance_class) \
                    .filter_by(id=self.instance_id) \
                    .first()
        return self._instance

    @deprecated(' `Do not use serialize inside model!` ')
    def serialize(self):
        serialized = attrs_to_dict(
            self,
            'id',
            'course_id',
            'module',
            'section_id',
            'visible',
        )
        if self.instance:
            serialized['type'] = self.instance.MODULE_TYPE
            if self.instance.MODULE_TYPE == 'STATEMENT':
                serialized['instance'] = attrs_to_dict(
                    self.instance,
                    'id',
                    'name',
                )
            elif self.instance.MODULE_TYPE in ['BOOK', 'MONITOR']:
                serialized['instance'] = self.instance.serialize(course_module_id=self.id)
            else:
                serialized['instance'] = self.instance.serialize()

        return serialized


class CourseModuleInstance(AbstractConcreteBase):
    MODULE = -1

    @declared_attr
    def id(cls):
        return db.Column(db.Integer)

    @declared_attr
    def name(cls):
        return db.Column(db.Unicode(255))

    @declared_attr
    def course_module(cls):
        class_name = cls.__name__
        class_module = cls.MODULE
        return db.relationship(
            CourseModule,
            primaryjoin=f'and_({class_name}.id==CourseModule.instance_id,'
                f'CourseModule.module=={class_module})',
            foreign_keys='%s.id' % cls.__name__,
        )

    @property
    def MODULE_TYPE(self):
        return type(self).__name__.upper()
