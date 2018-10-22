import json
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
)

from rmatics.model import db
from rmatics.model.role import RoleAssignment
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase


class TestAPI__statement_set_settings(TestCase):
    def setUp(self):
        super(TestAPI__statement_set_settings, self).setUp()

        self.create_roles()

        self.user = User()
        self.admin_user = User()

        self.statement = Statement()

        db.session.add_all((
            self.user,
            self.admin_user,
            self.statement,
        ))
        db.session.flush()

        role_assignment = RoleAssignment(
            user_id=self.admin_user.id,
            role_id=self.admin_role.id,
        )
        db.session.add(role_assignment)

    def send_request(self,
                     statement_id=None,
                     settings=None,
                     user=None,
                     ):
        if user:
            self.set_session({'user_id': user.id})
        response = self.client.post(
            f'/statement/{statement_id}/set_settings',
            data=json.dumps(settings),
            content_type='application/json',
        )
        return response

    def test_simple(self):
        settings = {
            'allowed_languages': [1, 2],
        }
        response = self.send_request(
            statement_id=self.statement.id,
            settings=settings,
            user=self.admin_user,
        )
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            has_entries({}),
        )

    def test_validation_error(self):
        settings = {
            'allowed_languages': 1,
        }
        response = self.send_request(
            statement_id=self.statement.id,
            settings=settings,
            user=self.admin_user,
        )
        assert_that(response.status_code, equal_to(400))
        assert_that(
            response.json,
            has_entries({
                'code': 400,
                'message': '1 is not of type \'array\'',
            }),
        )

    def test_unauthorized(self):
        response = self.send_request(
            statement_id=self.statement.id,
        )
        assert_that(response.status_code, equal_to(401))

    def test_forbidden(self):
        response = self.send_request(
            statement_id=self.statement.id,
            user=self.user,
        )
        assert_that(response.status_code, equal_to(403))

