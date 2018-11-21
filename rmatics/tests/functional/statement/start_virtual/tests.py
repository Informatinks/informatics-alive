import json
import time
from hamcrest import (
    assert_that,
    equal_to,
    close_to,
    has_entries,
)

from rmatics.model.base import db
from rmatics.model.course import Course
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase


class TestAPI__statement_start_virtual(TestCase):
    def setUp(self):
        super(TestAPI__statement_start_virtual, self).setUp()

        self.virtual_statement = Statement(
            virtual_olympiad=1,
            virtual_duration=300,
            time_start=0,
            time_stop=int(time.time()) + 100,
        )
        db.session.add(self.virtual_statement)

        self.user = User()
        db.session.add(self.user)
        db.session.flush()

    def test_simple(self):
        self.set_session({'user_id': self.user.id})
        response = self.client.post('/statement/1/start_virtual')
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            has_entries({
                'duration': self.virtual_statement.virtual_duration,
                'start': close_to(time.time(), 1),
            })
        )

    def test_with_password(self):
        password = 'secret'
        course = Course(password=password)
        db.session.add(course)
        self.virtual_statement.course = course

        self.set_session({'user_id': self.user.id})
        response = self.client.post('/statement/1/start_virtual')
        assert_that(response.status_code, equal_to(403))
        assert_that(
            response.json,
            has_entries({
                'code': 403,
                'message': 'Password is wrong or missing',
            })
        )

        response = self.client.post(
            '/statement/1/start_virtual',
            data=json.dumps({'password': 'wrong'}),
            content_type='application/json',
        )
        assert_that(response.status_code, equal_to(403))
        assert_that(
            response.json,
            has_entries({
                'code': 403,
                'message': 'Password is wrong or missing',
            })
        )

        response = self.client.post(
            '/statement/1/start_virtual',
            data=json.dumps({'password': password}),
            content_type='application/json',
        )
        assert_that(response.status_code, equal_to(200))
