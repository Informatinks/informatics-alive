from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.model import db
from rmatics.model.group_invite import GroupInvite
from rmatics.testutils import TestCase


class TestAPI__group_invite_get(TestCase):
    def setUp(self):
        super(TestAPI__group_invite_get, self).setUp()
        self.create_users()
        self.create_groups()

        self.group_invite = GroupInvite(
            group=self.groups[0],
            creator=self.users[0],
            redirect_type=GroupInvite.REDIRECT_COURSE,
            instance_id=123,
        )
        db.session.add(self.group_invite)
        db.session.flush()

    def send_request(self, user=None):
        if user:
            self.set_session({
                'user_id': user.id,
            })
        response = self.client.get('/group_invite')
        return response

    def test_simple(self):
        response = self.send_request(user=self.users[0])
        assert_that(
            response.json,
            equal_to(
                [
                    {
                        'group_id': self.groups[0].id,
                        'creator_id': self.users[0].id,
                        'redirect': {'course_id': 123},
                        'disabled': False,
                        'url': 'bcacbaabcaaaabc',
                    }
                ]
            )
        )

    def test_empty(self):
        response = self.send_request(user=self.users[1])
        assert_that(response.json, equal_to([]))

    def test_unauthorized(self):
        response = self.send_request()
        assert_that(response.status_code, equal_to(401))
        assert_that(
            response.json,
            equal_to({
                'code': 401,
                'message': 'Unauthorized',
            })
        )
