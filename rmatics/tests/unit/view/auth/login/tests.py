import json
import mock
from hamcrest import (
    assert_that,
    has_entries,
    equal_to,
    calling,
    raises,
)
from flask import (
    g,
    session
)


from rmatics.model import db
from rmatics.model.user import User
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import AuthWrongUsernameOrPassword
from rmatics.view.user.auth import auth_login


class TestView__auth_login(TestCase):
    def setUp(self):
        super(TestView__auth_login, self).setUp()
        self.username = 'some username'
        self.password = 'testtest'
        self.password_md5 = '05a671c66aefea124cc08b76ea6d30bb'
        self.user = User(
            id=123,
            username=self.username,
            password_md5=self.password_md5,
        )
        db.session.add(self.user)
    
    def call_view(self, data, exp_session, user=None):
        with self.app.test_request_context(data=json.dumps(data)):
            g.user = None
            exc = None
            try:
                result = auth_login()
            except Exception as e:
                exc = e
            assert_that(
                session,
                equal_to(exp_session),
            )
            if exc:
                raise exc

        return result


    def test_simple(self):
        with mock.patch('rmatics.view.user.auth.check_password', mock.Mock(return_value=True)) as mock_check_password:
            result = self.call_view(
                data={
                    'username': self.username,
                    'password': self.password,
                },
                exp_session={'user_id': self.user.id}
            )
        
        assert_that(
            result.json,
            has_entries({
                'id': self.user.id,
            })
        )
        mock_check_password.assert_called_once_with(self.password, self.password_md5)

    def test_no_user(self):
        with mock.patch('rmatics.view.user.auth.check_password', mock.Mock(return_value=True)):
            assert_that(
                calling(self.call_view).with_args(
                    data={
                        'username': 'bad username',
                        'password': '',
                    },
                    exp_session={},
                ),
                raises(AuthWrongUsernameOrPassword),
            )

    def test_wrong_password(self):
        with mock.patch('rmatics.view.user.auth.check_password', mock.Mock(return_value=False)):
            assert_that(
                calling(self.call_view).with_args(
                    data={
                        'username': self.username,
                        'password': 'bad password',
                    },
                    exp_session={},
                ),
                raises(AuthWrongUsernameOrPassword),
            )
