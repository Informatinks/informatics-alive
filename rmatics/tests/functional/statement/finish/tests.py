import time
from hamcrest import (
    assert_that,
    close_to,
    equal_to,
    has_entries,
)

from rmatics.model.base import db
from rmatics.model.participant import Participant
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase


class TestAPI__statement_finish(TestCase):
    def setUp(self):
        super(TestAPI__statement_finish, self).setUp()

        self.user = User()
        db.session.add(self.user)

        self.now = time.time()
        self.duration = 290
        self.statement = Statement(
            olympiad=1,
            time_start=self.now - 10,
            time_stop=self.now + self.duration,
        )
        db.session.add(self.statement)
        db.session.flush()

        self.actual_duration = 5
        self.participant = Participant(
            user_id=self.user.id,
            statement_id=self.statement.id,
            start=int(self.now - self.actual_duration),
            duration=self.duration,
        )
        db.session.add(self.participant)

    def test_simple(self):
        self.set_session({'user_id': self.user.id})
        response = self.client.post(f'/statement/{self.statement.id}/finish')
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            has_entries({
                'statement_id': self.statement.id,
                'start': int(self.now - self.actual_duration),
                'duration': close_to(self.actual_duration, 1),
            })
        )
