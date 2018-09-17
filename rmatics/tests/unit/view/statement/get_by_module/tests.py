import mock
from hamcrest import (
    assert_that,
    has_entries,
)

from rmatics.model import db
from rmatics.model.course_module import CourseModule
from rmatics.model.statement import Statement
from rmatics.testutils import TestCase
from rmatics.view.statement import statement_get_by_module


class TestView__statement_get_by_module(TestCase):
    def setUp(self):
        super(TestView__statement_get_by_module, self).setUp()

        self.statement = Statement()
        db.session.add(self.statement)
        db.session.flush()

        self.course_module = CourseModule(
            id=123,
            instance_id=self.statement.id,
            module=19,
        )
        db.session.add(self.course_module)
        db.session.flush()

    def test_simple(self):
        query_string = {'course_module_id': self.course_module.id}
        with self.app.test_request_context(query_string=query_string):
            response = statement_get_by_module()
            assert_that(
                response.json,
                has_entries({
                    'id': self.statement.id,
                })
            )
