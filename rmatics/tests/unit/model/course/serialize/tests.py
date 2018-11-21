from hamcrest import (
    assert_that,
    has_entries,
)

from rmatics.model.base import db
from rmatics.model.course import Course
from rmatics.testutils import TestCase


class TestModel__course_serialize(TestCase):
    def setUp(self):
        super(TestModel__course_serialize, self).setUp()

        self.course = Course(
            id=123,
            full_name='full name',
            short_name='short name',
        )
        db.session.add(self.course)

    def test_without_password(self):
        assert_that(
            self.course.serialize(),
            has_entries({
                'id': self.course.id,
                'full_name': self.course.full_name,
                'short_name': self.course.short_name,
                'require_password': False,
            })
        )

    def test_with_password(self):
        self.course.password = 'secret'
        assert_that(
            self.course.serialize(),
            has_entries({
                'id': self.course.id,
                'full_name': self.course.full_name,
                'short_name': self.course.short_name,
                'require_password': True,
            })
        )
