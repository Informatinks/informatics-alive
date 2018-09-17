import mock
import time
from hamcrest import (
    assert_that,
    calling,
    close_to,
    equal_to,
    raises,
)

from rmatics.model import db
from rmatics.model.participant import Participant
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import (
    StatementNothingToFinish,
)


class TestModel__statement_finish_participant(TestCase):
    def setUp(self):
        super(TestModel__statement_finish_participant, self).setUp()

        self.create_statements()

        self.now = int(time.time())
        self.duration = 10

        self.user = User()
        db.session.add(self.user)

        db.session.flush()

    def test_simple(self):
        participant = Participant(
            user_id=self.user.id,
            statement_id=self.statements[0].id,
            start=self.now - self.duration,
            duration = self.duration * 2,
        )
        db.session.add(participant)
        finished = self.statements[0].finish_participant(self.user)
        assert_that(
            finished.user_id,
            equal_to(self.user.id)
        )
        assert_that(
            finished.statement_id,
            equal_to(self.statements[0].id)
        )
        assert_that(
            finished.start,
            equal_to(self.now - self.duration)
        )
        assert_that(
            finished.duration,
            close_to(self.duration, 2)
        )

        db_participant = db.session.query(Participant).filter(
            Participant.user_id == self.user.id
        ).filter(
            Participant.statement_id == self.statements[0].id
        ).filter(
            Participant.start == self.now - self.duration
        ).one()
        assert_that(
            db_participant.duration,
            equal_to(finished.duration)
        )

    def test_no_active_participant(self):
        assert_that(
            calling(self.statements[0].finish_participant).with_args(self.user),
            raises(StatementNothingToFinish)
        )

    def test_active_participant_for_other_statement(self):
        assert_that(
            calling(self.statements[1].finish_participant).with_args(self.user),
            raises(StatementNothingToFinish)
        )
