from hamcrest import (
    assert_that,
    has_entries,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.group import Group
from rmatics.testutils import TestCase


class TestAPI__group_search(TestCase):
    def setUp(self):
        super(TestAPI__group_search, self).setUp()

        self.groups = [
            Group(name='group 1', visible=True),
            Group(name='group 2', visible=True),
            Group(name='aaaaaaa', visible=True),
            Group(name='bbbbbbb', visible=True),
            Group(name='ccccccc', visible=True),
            Group(name='ddddddd', visible=True),
        ]
        db.session.add_all(self.groups)
        db.session.flush()

    def send_request(self, name=None):
        url = '/group'
        if name is not None:
            url += '?name=' + name

        return self.client.get(url)

    def test_simple(self):
        response = self.send_request('group')
        assert_that(
            response.json,
            has_entries({
                '1': has_entries({
                    'name': 'group 1',
                }),
                '2': has_entries({
                    'name': 'group 2'
                }),
            })
        )

    def test_empty(self):
        response = self.send_request('xxxxxxx')
        assert_that(
            response.json,
            equal_to({})
        )

    def test_limit(self):
        response = self.send_request()
        assert_that(
            len(response.json.keys()),
            equal_to(5)
        )

    def test_skips_invisible(self):
        name = 'invisible'
        invisible_group = Group(name=name, visible=False)
        db.session.add(invisible_group)
        db.session.flush()

        response = self.send_request(name)
        assert_that(response.json, equal_to({}))
