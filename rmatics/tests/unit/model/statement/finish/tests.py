import time
import mock

from rmatics.model.base import db
from rmatics.model.statement import Statement
from rmatics.model.user import User
from rmatics.testutils import TestCase


class TestModel__statement_finish(TestCase):
    def setUp(self):
        super(TestModel__statement_finish, self).setUp()

        self.now = int(time.time())
        self.time_start = self.now - 60
        self.time_stop = self.now + 30

        self.statement = Statement(
            olympiad=1,
            time_start=self.time_start,
            time_stop=self.time_stop,
        )
        db.session.add(self.statement)

        self.user = User()
        db.session.add(self.user)

        db.session.flush()

    def test_simple(self):
        with mock.patch('rmatics.model.statement.Statement.finish_participant', mock.Mock()) as mock_finish:
            self.statement.finish(self.user)
        mock_finish.assert_called_once_with(self.user)
