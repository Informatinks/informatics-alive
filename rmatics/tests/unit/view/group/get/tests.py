import mock
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    raises,
)

from rmatics.model.group import Group
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import GroupNotFound
from rmatics.view.user.group import group_get


class TestView__group_get(TestCase):
    def setUp(self):
        super(TestView__group_get, self).setUp()

        self.create_groups()

    def call_view(self, group_id):
        serialize_mock = mock.Mock(return_value='serialized')
        with mock.patch.object(Group, 'serialize', serialize_mock):
            with self.app.test_request_context():
                result = group_get(group_id)

        serialize_mock.assert_called_once()
        assert_that(result.json, equal_to('serialized'))

        return result

    def test_simple(self):
        self.call_view(1)

    def test_not_found(self):
        assert_that(
            calling(self.call_view).with_args(123),
            raises(GroupNotFound)
        )
