from flask import g
from hamcrest import (
    assert_that,
    calling,
    raises,
)

from rmatics.model.base import db
from rmatics.model.user import User
from rmatics.testutils import TestCase
from werkzeug.exceptions import Unauthorized
from rmatics.view.user.auth import auth_logout


class TestView__auth_logout(TestCase):
    def setUp(self):
        super(TestView__auth_logout, self).setUp()
        self.user = User()
        db.session.add(self.user)
        db.session.flush()

    def test_simple(self):
        with self.app.test_request_context():
            g.user = self.user
            auth_logout()

    def test_logged_out(self):
        assert_that(
            calling(auth_logout),
            raises(Unauthorized),
        )
