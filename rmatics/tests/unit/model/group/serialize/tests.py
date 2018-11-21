import mock
from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.group import Group
from rmatics.testutils import TestCase


class TestModel__group_serialize(TestCase):
    def test_simple(self):
        self.create_users()
        group = Group(
            name='1',
            description='2',
            owner=self.users[0],
            visible=True,
        )
        db.session.add(group)
        db.session.flush()

        assert_that(
            group.serialize(),
            equal_to({
                'name': '1',
                'description': '2',
                'owner_id': self.users[0].id,
                'visible': True,
            })
        )
