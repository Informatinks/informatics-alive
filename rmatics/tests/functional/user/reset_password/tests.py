import json
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
    anything,
)


from rmatics.model import db
from rmatics.model.user import User
from rmatics.model.role import (
    Role,
    RoleAssignment,
)
from rmatics.testutils import TestCase


class TestAPI__user_reset_password(TestCase):
    def setUp(self):
        super(TestAPI__user_reset_password, self).setUp()

        self.create_roles()

        self.user = User()
        self.admin_user = User()
        db.session.add_all((self.user, self.admin_user))
        db.session.flush()

        role_assignment = RoleAssignment(
            role_id=self.admin_role.id,
            user_id=self.admin_user.id,
        )
        db.session.add(role_assignment)


    def send_request(self,
                     user_id=None,
                     session_user_id=None,
                     ):
        if session_user_id:
            self.set_session({'user_id': session_user_id})
        response = self.client.post(
            '/user/reset_password',
            data=json.dumps({
                'id': user_id,
            }),
        )
        return response

    def test_simple(self):
        response = self.send_request(
            session_user_id=self.admin_user.id,
            user_id=self.user.id,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            has_entries({
                'id': self.user.id,
                'password': anything(),
            })
        )

    def test_no_user(self):
        response = self.send_request(
            session_user_id=self.admin_user.id,
            user_id=1111,
        )
        assert_that(response.status_code, equal_to(404))
        assert_that(
            response.json,
            has_entries({
                'code': 404,
                'message': 'No such user',
            })
        )

    def test_not_admin(self):
        response = self.send_request(
            session_user_id=self.user.id,
            user_id=self.admin_user.id,
        )
        assert_that(response.status_code, equal_to(403))
        assert_that(
            response.json,
            has_entries({
                'code': 403,
                'message': 'Forbidden',
            })
        )

    def test_not_authorized(self):
        response = self.send_request(
            user_id=self.user.id,
        )
        assert_that(response.status_code, equal_to(401))
        assert_that(
            response.json,
            has_entries({
                'code': 401,
                'message': 'Unauthorized',
            })
        )
