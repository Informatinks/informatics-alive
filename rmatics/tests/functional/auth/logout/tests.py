from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    calling,
    raises,
    is_not,
    has_items,
)

from rmatics.model import db
from rmatics.model.user import User
from rmatics.testutils import TestCase
from rmatics.utils.functions import attrs_to_dict


class TestAPI__auth_logout(TestCase):
    def setUp(self):
        super(TestAPI__auth_logout, self).setUp()

        self.username = 'some username'
        self.password = 'testtest'
        self.password_md5 = '05a671c66aefea124cc08b76ea6d30bb'

        self.user = User(
            username=self.username,
            password=self.password_md5,
            firstname='some firstname',
            lastname='some lastname'
        )
        db.session.add(self.user)
        db.session.flush()

    def send_request(self):
        return self.client.post('/auth/logout')

    def check_request(self,
                      status_code=200
                      ):
        response = self.send_request()

        if status_code != 200:
            assert_that(
                response.json,
                has_entries({
                    'code': status_code,
                })
            )
            return

        assert_that(
            response.json,
            equal_to({})
        )

        # В сессии больше нет user_id
        assert_that(
            self.get_session(),
            has_entries({
                'user_id': None,
            })
        )

    def test_simple(self):
        self.set_session({'user_id': self.user.id})
        self.check_request()

    def test_logged_out(self):
        self.check_request(
            status_code=401,
        )

    def test_bad_login(self):
        self.set_session({'user_id': 'bad user_id'})
        self.check_request(
            status_code=401,
        )
