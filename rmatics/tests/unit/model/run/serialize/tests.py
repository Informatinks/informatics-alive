import datetime
import mock
from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.run import Run
from rmatics.testutils import TestCase


class TestModel__run_serialize(TestCase):
    def setUp(self):
        super(TestModel__run_serialize, self).setUp()

        self.create_ejudge_problems()
        self.create_statements()
        self.create_users()

    def test_simple(self):
        run = Run(
            user=self.users[0],
            problem=self.ejudge_problems[0],
            statement=self.statements[0],
            score=123,
            create_time=datetime.datetime(2018, 3, 24, 10, 49, 0),
            ejudge_score=456,
            ejudge_status=7,
            ejudge_language_id=27,
            ejudge_create_time=datetime.datetime(2010, 1, 1, 1, 1, 1)
        )
        db.session.add(run)
        db.session.flush()

        assert_that(
            run.serialize(),
            equal_to({
                'id': 1,
                'create_time': '2018-03-24 10:49:00',
                'ejudge_contest_id': None,
                'ejudge_run_id': None,
                'problem_id': self.ejudge_problems[0].id,
                'statement_id': self.statements[0].id,
                'score': 123,
                'status': 7,
                'language_id': 27,
                'user': {
                    'id': 1,
                    'ejudge_id': 179,
                    'firstname': 'Maxim',
                    'lastname': 'Grishkin',
                }
            })
        )
