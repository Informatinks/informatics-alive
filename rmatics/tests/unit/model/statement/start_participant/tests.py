import mock
import time
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    is_not,
    raises,
)

from rmatics.model.base import db
from rmatics.model.course import Course
from rmatics.model.participant import Participant
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import (
    StatementCanOnlyStartOnce,
    StatementOnlyOneOngoing,
    StatementPasswordIsWrong,
)


class TestModel__statement_start_participant(TestCase):
    def setUp(self):
        super(TestModel__statement_start_participant, self).setUp()

        self.create_statements()

        self.now = int(time.time())
        self.duration = 10

        self.user = User()
        db.session.add(self.user)

        self.time_start = self.now
        self.time_stop = self.now + 100
        self.statement = Statement(
            time_start=self.time_start,
            time_stop=self.time_stop,
        )
        db.session.add(self.statement)

        db.session.flush()

    def test_simple(self):
        with mock.patch('rmatics.model.statement.time.time', mock.Mock(return_value=self.now)):
            participant = self.statement.start_participant(
                user=self.user,
                duration=self.duration,
            )
        assert_that(
            participant.user_id,
            equal_to(self.user.id)
        )
        assert_that(
            participant.statement_id,
            equal_to(self.statement.id)
        )
        assert_that(
            participant.start,
            equal_to(self.now)
        )
        assert_that(
            participant.duration,
            equal_to(self.duration)
        )
        db.session.query(Participant) \
            .filter_by(user_id=self.user.id) \
            .filter_by(statement_id=self.statement.id) \
            .filter_by(start=self.now) \
            .filter_by(duration=self.duration) \
            .one()

    def test_can_only_start_once(self):
        participant = Participant(
            user_id=self.user.id,
            statement_id=self.statement.id,
            start=self.now - self.duration,
            duration = self.duration,
        )
        db.session.add(participant)
        assert_that(
            calling(self.statement.start_participant).with_args(
                user=self.user,
                duration=self.duration,
            ),
            raises(StatementCanOnlyStartOnce)
        )

    def test_only_one_ongoing(self):
        participant = Participant(
            user_id=self.user.id,
            statement_id=self.statements[0].id,
            start=self.now - self.duration,
            duration=self.duration * 2,
        )
        db.session.add(participant)
        assert_that(
            calling(self.statement.start_participant).with_args(
                user=self.user,
                duration=self.duration,
            ),
            raises(StatementOnlyOneOngoing)
        )

    def test_with_password(self):
        password = 'secret'
        course = Course(password=password)
        db.session.add(course)
        self.statement.course = course

        with mock.patch('rmatics.model.statement.time.time', mock.Mock(return_value=self.now)):
            assert_that(
                calling(self.statement.start_participant).with_args(
                    user=self.user,
                    duration=self.duration,
                ),
                raises(StatementPasswordIsWrong)
            )
            assert_that(
                calling(self.statement.start_participant).with_args(
                    user=self.user,
                    duration=self.duration,
                    password='wrong',
                ),
                raises(StatementPasswordIsWrong)
            )
            assert_that(
                calling(self.statement.start_participant).with_args(
                    user=self.user,
                    duration=self.duration,
                    password=password,
                ),
                is_not(raises(StatementPasswordIsWrong))
            )


