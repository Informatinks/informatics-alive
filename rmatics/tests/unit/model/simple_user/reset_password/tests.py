import mock
from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.user import SimpleUser
from rmatics.testutils import TestCase


class TestModel__simple_user_rest_password(TestCase):
    def setUp(self):
        super(TestModel__simple_user_rest_password, self).setUp()

        self.simple_user = SimpleUser()
        db.session.add(self.simple_user)

    def test_simple(self):
        password = 'some password'
        hashed_password = 'hashed password'
        with mock.patch('rmatics.model.user.random_password', mock.Mock(return_value=password)), \
                mock.patch('rmatics.model.user.hash_password', mock.Mock(return_value=hashed_password)):
            assert_that(
                self.simple_user.reset_password(),
                equal_to(password)
            )
            assert_that(
                self.simple_user.password_md5,
                equal_to(hashed_password)
            )
