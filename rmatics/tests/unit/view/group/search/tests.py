import mock
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.group import Group
from rmatics.testutils import TestCase
from rmatics.view.user.group import group_search


class TestView__group_search(TestCase):
    def setUp(self):
        super(TestView__group_search, self).setUp()

        self.groups = [
            Group(name='group 1', visible=True),
            Group(name='group 2', visible=True),
            Group(name='group 3', visible=True),
            Group(name='aa', visible=True),
            Group(name='bb', visible=True),
            Group(name='cc', visible=True),
            Group(name='invisible', visible=False),
        ]
        db.session.add_all(self.groups)
        db.session.flush()

    def call_view(self, name=None):
        serialize_mock = mock.Mock(return_value='serialized')

        query_string = f'name={name}' if name is not None else None

        with mock.patch.object(Group, 'serialize', serialize_mock):
            with self.app.test_request_context(query_string=query_string):
                response = group_search()

        assert_that(response.status_code, equal_to(200))
        result = response.json

        for group_id in result:
            assert_that(result[group_id], equal_to('serialized'))

        return result

    def test_multiple(self):
        result = self.call_view('group')
        assert_that(result.keys(), contains_inanyorder('1', '2', '3'))

    def test_single(self):
        result = self.call_view('group 3')
        assert_that(result.keys(), contains_inanyorder('3'))

    def test_empty(self):
        result = self.call_view('abacaba')
        assert_that(result, equal_to({}))

    def test_limit_and_order(self):
        result = self.call_view()
        assert_that(result.keys(), contains_inanyorder('1', '2', '3', '4', '5'))

    def test_invisible(self):
        result = self.call_view(self.groups[-1].name)
        assert_that(result, equal_to({}))
