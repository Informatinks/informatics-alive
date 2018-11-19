import json
import mock
from flask import g
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_entries,
    raises,
)

from rmatics.model import db
from rmatics.model.user import User
from rmatics.model.role import RoleAssignment
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import UserNotFound
from rmatics.view.user.user import user_reset_password


class TestView__user_reset_password(TestCase):
    def setUp(self):
        super(TestView__user_reset_password, self).setUp()

        self.create_users()
        self.create_roles()

        role_assignment = RoleAssignment(
            role=self.admin_role,
            user_id=self.users[0].id,
        )
        db.session.add(role_assignment)
        db.session.flush()

        self.password_md5 = 'some md5'
        self.user = User(password_md5=self.password_md5)

        db.session.add(self.user)
        db.session.flush()

    def test_simple(self):
        new_password = 'some password'
        with mock.patch('rmatics.view.user.user.User.reset_password', mock.Mock()) as mock_reset_password:
            mock_reset_password.return_value = new_password
            with self.app.test_request_context(data=json.dumps({'id': self.user.id})):
                g.user = self.users[0]
                response = user_reset_password()

        mock_reset_password.assert_called_once()
        assert_that(
            response.json,
            has_entries({
                'id': self.user.id,
                'password': new_password,
            })
        )

    def test_no_user(self):
        with self.app.test_request_context(data=json.dumps({'id': 123})):
            g.user = self.users[0]
            assert_that(
                calling(user_reset_password),
                raises(UserNotFound)
            )
            assert_that(
                self.user.password_md5,
                equal_to(self.password_md5),
            )
