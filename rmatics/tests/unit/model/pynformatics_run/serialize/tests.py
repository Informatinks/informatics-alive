import mock
from flask import g
from hamcrest import (
    assert_that,
    is_not,
    has_entries,
    has_key,
)

from rmatics.model import db
from rmatics.model.pynformatics_run import PynformaticsRun
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.user import SimpleUser
from rmatics.testutils import TestCase


class TestModel__pynformatics_run__serialize(TestCase):
    def setUp(self):
        super(TestModel__pynformatics_run__serialize, self).setUp()

        self.create_statements()

        self.author = SimpleUser(ejudge_id=666)
        self.other = SimpleUser(ejudge_id=777)
        self.run = EjudgeRun(
            run_id=1,
            contest_id=2,
            user=self.author,
        )
        self.pynformatics_run = PynformaticsRun(
            run=self.run,
            statement=self.statements[0],
            source='some source',
        )

        db.session.add_all([
            self.author,
            self.other,
            self.run,
            self.pynformatics_run
        ])
        db.session.flush()

    def test_for_author(self):
        with self.app.test_request_context():
            g.user = self.author
            result = self.pynformatics_run.serialize()
        assert_that(
            result,
            has_entries({
                'statement_id': self.pynformatics_run.statement_id,
                'source': self.pynformatics_run.source,
            })
        )

    def test_for_other(self):
        with self.app.test_request_context():
            g.user = self.other
            result = self.pynformatics_run.serialize()
        assert_that(
            result,
            has_entries({
                'statement_id': self.pynformatics_run.statement_id,
            })
        )
        assert_that(
            result,
            is_not(has_key('source'))
        )
