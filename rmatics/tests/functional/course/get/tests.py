from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    has_items,
    is_not,
)

from rmatics.model import db
from rmatics.model.course import Course
from rmatics.testutils import TestCase


class TestAPI__course_get(TestCase):
    def setUp(self):
        super(TestAPI__course_get, self).setUp()

        self.course = Course(
            id=123,
            short_name='course',
            full_name='course course',
        )
        db.session.add(self.course)
        db.session.flush()

    def test_simple(self):
        response = self.client.get('/course/123')
        assert_that(response.status_code, equal_to(200))
        self.assertIn('data', response.json)
        data = response.json['data']
        assert_that(
            data,
            equal_to({
                'id': 123,
                'full_name': 'course course',
                'short_name': 'course',
                'require_password': False,
                'sections': [],
            })
        )

    def test_password(self):
        self.course.password = 'abc'
        response = self.client.get('/course/123')
        assert_that(response.status_code, equal_to(200))
        self.assertIn('data', response.json)
        data = response.json['data']
        assert_that(
            data,
            has_entries({'require_password': True}),
        )
        assert_that(
            response.json,
            is_not(has_items('sections')),
        )

    def test_not_found(self):
        response = self.client.get('/course/456')
        assert_that(response.status_code, equal_to(404))
        assert_that(
            response.json,
            equal_to({
                'code': 404,
                'message': 'Course with this id is not found',
                'result': 'error',
            })
        )