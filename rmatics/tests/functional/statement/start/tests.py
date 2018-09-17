import json
import time
from hamcrest import (
    assert_that,
    close_to,
    equal_to,
    has_entries,
)

from rmatics.model import db
from rmatics.model.course import Course
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase


class TestAPI__statement_start(TestCase):
    def setUp(self):
        super(TestAPI__statement_start, self).setUp()

        self.user = User()
        db.session.add(self.user)

        self.now = time.time()
        self.duration = 290
        self.statement = Statement(
            olympiad=1,
            time_start=self.now - 10,
            time_stop=self.now + self.duration,
        )
        db.session.add(self.statement)
        db.session.flush()

    def test_simple(self):
        self.set_session({'user_id': self.user.id})
        response = self.client.post(f'/statement/{self.statement.id}/start')
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            has_entries({
                'statement_id': self.statement.id,
                'start': close_to(self.now, 1),
                'duration': close_to(self.duration, 1),
            })
        )

    def test_with_password(self):
        password = 'secret'
        course = Course(password=password)
        db.session.add(course)
        self.statement.course = course

        self.set_session({'user_id': self.user.id})
        response = self.client.post(f'/statement/{self.statement.id}/start')
        assert_that(response.status_code, equal_to(403))
        assert_that(
            response.json,
            has_entries({
                'code': 403,
                'message': 'Password is wrong or missing'
            })
        )

        response = self.client.post(
            f'/statement/{self.statement.id}/start',
            data=json.dumps({'password': 'wrong'}),
            content_type='application/json',
        )
        assert_that(response.status_code, equal_to(403))
        assert_that(
            response.json,
            has_entries({
                'code': 403,
                'message': 'Password is wrong or missing'
            })
        )

        response = self.client.post(
            f'/statement/{self.statement.id}/start',
            data=json.dumps({'password': password}),
            content_type='application/json',
        )
        assert_that(response.status_code, equal_to(200))
