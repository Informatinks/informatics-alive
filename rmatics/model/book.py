from sqlalchemy.dialects.mysql import MEDIUMTEXT

from rmatics.model.base import db
from rmatics.model.course_module import CourseModuleInstance
from rmatics.utils.functions import attrs_to_dict


class Book(CourseModuleInstance, db.Model):
    """
    Модуль курса, описывающий книгу
    """
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'mdl_book'
    __mapper_args__ = {
        'polymorphic_identity': 'book',
        'concrete': True,
    }

    MODULE = 18

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column('course', db.Integer)
    name = db.Column(db.Unicode(255))
    summary = db.Column(MEDIUMTEXT)

    @staticmethod
    def url(course_module_id):
        return f'http://informatics.msk.ru/mod/book/view.php?id={course_module_id}'

    def serialize(self, course_module_id=None):
        serialized = attrs_to_dict(
            self,
            'id',
            'course_id',
            'name',
        )
        if course_module_id:
            serialized['url'] = Book.url(course_module_id)
        return serialized
