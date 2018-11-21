import mock
import time
from hamcrest import (
    assert_that,
    calling,
    close_to,
    equal_to,
    raises,
)

from rmatics.model.base import db
from rmatics.model.participant import Participant
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import (
    StatementNothingToFinish,
)


class TestModel__Statement_finish_virtual(TestCase):
    def setUp(self):
        super(TestModel__Statement_finish_virtual, self).setUp()

        self.now = int(time.time())
        self.virtual_duration = 100
        self.time_start = self.now - 60
        self.statement = Statement(
            virtual_olympiad=1,
            virtual_duration=self.virtual_duration,
            time_start=self.time_start,
        )
        db.session.add(self.statement)

        self.user = User()
        db.session.add(self.user)

        db.session.flush()

    def test_simple(self):
        with mock.patch('rmatics.model.statement.Statement.finish_participant', mock.Mock()) as mock_finish:
            self.statement.finish_virtual(self.user)
        mock_finish.assert_called_once_with(self.user)
