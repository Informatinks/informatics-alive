from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.group import Group
from rmatics.testutils import TestCase


class TestAPI__group_get(TestCase):
    def setUp(self):
        super(TestAPI__group_get, self).setUp()
        self.create_groups()

    def send_request(self, group_id):
        return self.client.get(f'/group/{group_id}')

    def test_simple(self):
        response = self.send_request(1)
        assert_that(
            response.json,
            equal_to({
                'name': 'group 1',
                'visible': 1,
                'description': None,
                'owner_id': None,
            })
        )

    def test_not_found(self):
        response = self.send_request(179)
        assert_that(response.status_code, equal_to(404))
        assert_that(
            response.json,
            equal_to({
                'code': 404,
                'message': 'Group not found',
                'status': 'error',
            })
        )

    def test_invisible_not_found(self):
        invisible_group = Group(visible=False)
        db.session.add(invisible_group)
        db.session.flush()

        response = self.send_request(invisible_group.id)
        assert_that(response.status_code, equal_to(404))
        assert_that(
            response.json,
            equal_to({
                'code': 404,
                'message': 'Group not found',
                'status': 'error',
            })
        )
