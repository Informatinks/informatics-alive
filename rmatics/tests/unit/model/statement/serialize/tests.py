import mock
from flask import g
from hamcrest import (
    assert_that,
    anything,
    has_entries,
    has_items,
    is_not,
)

from rmatics.model import db
from rmatics.model.course import Course
from rmatics.model.course_module import CourseModule
from rmatics.model.participant import Participant
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase


class TestModel__statement_serialize(TestCase):
    def setUp(self):
        super(TestModel__statement_serialize, self).setUp()

        self.course = Course(id=123)
        db.session.add(self.course)

        self.statement = Statement(course=self.course)
        self.user = User()

        db.session.add_all([self.statement, self.user])
        db.session.flush()

        self.course_module = CourseModule(
            instance_id=self.statement.id,
            module=19,
            course_id=self.course.id,
        )

        self.participant = Participant(
            user_id=self.user.id,
            statement_id=self.statement.id,
        )

        db.session.add_all([self.course_module, self.participant])


    def test_simple(self):
        assert_that(
            self.statement.serialize(),
            has_entries({
                'course': anything(),
                'course_module_id': 1,
                'id': self.statement.id,
                'name': None,
                'olympiad': None,
                'problems': {},
                'settings': None,
                'time_start': None,
                'time_stop': None,
                'virtual_duration': None,
                'virtual_olympiad': None,
            })
        )

    def test_olympiad(self):
        self.statement.olympiad = True
        with self.app.test_request_context():
            g.user = None
            assert_that(
                self.statement.serialize(),
                is_not(has_items('problems'))
            )
        with self.app.test_request_context():
            g.user = self.user
            assert_that(
                self.statement.serialize(),
                has_items('problems')
            )

    def test_virtual_olympiad(self):
        self.statement.virtual_olympiad = True
        with self.app.test_request_context():
            g.user = None
            assert_that(
                self.statement.serialize(),
                is_not(has_items('problems'))
            )
        with self.app.test_request_context():
            g.user = self.user
            assert_that(
                self.statement.serialize(),
                has_items('problems')
            )
