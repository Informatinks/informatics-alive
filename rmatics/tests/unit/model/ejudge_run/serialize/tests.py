import mock
from flask import g
from hamcrest import (
    assert_that,
    has_entries,
    has_key,
    is_not,
)

from rmatics.model.base import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.user import SimpleUser
from rmatics.testutils import TestCase


class TestModel__ejudge_run_serialize(TestCase):
    def setUp(self):
        super(TestModel__ejudge_run_serialize, self).setUp()

        self.create_problems()

        self.author = SimpleUser(
            ejudge_id=1,
            firstname='author_firstname',
            lastname='author_lastname',
        )
        self.other = SimpleUser(
            ejudge_id=2,
            firstname='other_firstname',
            lastname='other_lastname',
        )
        db.session.add_all([self.author, self.other])
        db.session.flush()

        self.run = EjudgeRun(
            user=self.author,
            run_id=123,
            problem=self.problems[0],
        )
        db.session.add(self.run)
        db.session.flush([self.run])

        self.pynformatics_run_serialized = {'some_key': 'some_value'}
        self.pynformatics_run_mock = mock.Mock()
        self.pynformatics_run_mock.serialize = mock.Mock(return_value=self.pynformatics_run_serialized)

    def call_serialize(self):
        with mock.patch(
                'rmatics.model.ejudge_run.EjudgeRun.get_pynformatics_run',
                mock.Mock(return_value=self.pynformatics_run_mock)
        ):
            return self.run.serialize()


    def test_for_author(self):
        with self.app.test_request_context():
            g.user = self.author
            result = self.call_serialize()
        assert_that(
            result,
            has_entries({
                'status': None,
                'contest_id': self.run.contest_id,
                'prob_id': 1,
                'run_id': self.run.run_id,
                'create_time': 'None',
                'lang_id': None,
                'score': None,
                'size': None,
            })
        )
        assert_that(
            result,
            has_entries(self.pynformatics_run_serialized)
        )
        assert_that(
            result,
            is_not(has_key('user'))
        )

    def test_for_other(self):
        with self.app.test_request_context():
            g.user = self.other
            result = self.call_serialize()
        assert_that(
            result,
            has_entries({
                'status': None,
                'contest_id': self.run.contest_id,
                'prob_id': 1,
                'run_id': self.run.run_id,
                'create_time': 'None',
                'lang_id': None,
                'score': None,
                'size': None,
                'user': self.author.serialize()
            })
        )
