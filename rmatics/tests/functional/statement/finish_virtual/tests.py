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


class TestAPI__statement_finish_virtual(TestCase):
    def setUp(self):
        super(TestAPI__statement_finish_virtual, self).setUp()

        self.virtual_statement = Statement(
            virtual_olympiad=1,
            virtual_duration=300,
        )
        db.session.add(self.virtual_statement)

        self.user = User()
        db.session.add(self.user)
        db.session.flush()

        self.actual_duration = 10
        self.participant = Participant(
            user_id=self.user.id,
            statement_id=self.virtual_statement.id,
            start=time.time() - self.actual_duration,
            duration=300,
        )
        db.session.add(self.participant)

    def test_simple(self):
        self.set_session({'user_id': self.user.id})
        response = self.client.post('/statement/1/finish_virtual')
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            has_entries({
                'duration': close_to(self.actual_duration, 1),
                'start': self.participant.start,
            })
        )
