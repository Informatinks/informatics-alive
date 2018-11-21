import time
from hamcrest import (
    assert_that,
    equal_to,
    has_entries,
)

from rmatics.model.base import db
from rmatics.model.user import SimpleUser
from rmatics.model.participant import Participant
from rmatics.testutils import TestCase


class TestAPI__bootstrap(TestCase):
    def setUp(self):
        super(TestAPI__bootstrap, self).setUp()
        self.create_users()
        self.create_statements()

    def test_simple(self):
        self.set_session({'user_id': self.users[0].id})
        response = self.client.get('/bootstrap')
        assert_that(
            response.json,
            has_entries({
                'user': {
                    'id': self.users[0].id,
                    'firstname': self.users[0].firstname,
                    'lastname': self.users[0].lastname,
                    'ejudge_id': self.users[0].ejudge_id,
                }
            })
        )

    def test_with_active_virtual(self):
        participant = Participant(
            user=self.users[0],
            statement=self.statements[0],
            start=int(time.time()),
            duration=456,
        )
        db.session.add(participant)

        self.set_session({'user_id': self.users[0].id})
        response = self.client.get('/bootstrap')

        assert_that(
            response.json,
            has_entries({
                'user': has_entries({
                    'active_virtual': {
                        'start': participant.start,
                        'duration': participant.duration,
                        'statement_id': participant.statement_id,
                    }
                }),
            })
        )
