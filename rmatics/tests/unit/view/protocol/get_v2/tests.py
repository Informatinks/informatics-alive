import mock
from flask import g
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_entries,
    raises,
)

from rmatics.model.base import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.problem import EjudgeProblem
from rmatics.model.user import SimpleUser
from rmatics.testutils import TestCase
from werkzeug.exceptions import InternalServerError
from rmatics.utils.exceptions import (
    RunAuthorOnly,
    RunNotFound,
)
from rmatics.view.protocol import protocol_get_v2


class TestView__protocol_get_v2(TestCase):
    def setUp(self):
        super(TestView__protocol_get_v2, self).setUp()

        self.user = SimpleUser(ejudge_id=22)
        db.session.add(self.user)
        db.session.flush()

        self.run_id = 123
        self.contest_id = 456

        self.problem = EjudgeProblem(
            ejudge_prid=1,
            contest_id=2,
            ejudge_contest_id=self.contest_id,
            problem_id=4,
        )
        db.session.add(self.problem)
        db.session.flush()

        self.run = EjudgeRun(
            run_id=self.run_id,
            problem=self.problem,
            user_id=self.user.ejudge_id,
        )

        db.session.add(self.run)
        db.session.flush()

    def call_view(self,
                  run_id=None,
                  contest_id=None,
                  ):
        with self.app.test_request_context():
            g.user = self.user
            return protocol_get_v2(
                contest_id=contest_id or self.contest_id,
                run_id=run_id or self.run_id,
            )

    def test_simple(self):
        # Тесты 1 и 3 являются тестами из условия, поэтому для них должен быть вызван отдельный метод, который выдаст
        # полный протокол
        tests = {
            '1': 'first',
            '2': 'second',
            '3': 'third',
            '4': 'forth',
        }
        host = 'some host'
        compiler_output = 'some compiler output'

        def fetch_mock_data(self):
            self.tests = tests
            self.host = host
            self.compiler_output = compiler_output

        def get_mock_full_protocol(self, str_num):
            return 'full %s' % str_num

        self.problem.sample_tests = '1,3'
        db.session.flush()

        with mock.patch('rmatics.model.ejudge_run.EjudgeRun.fetch_tested_protocol_data', autospec=True) as fetch_protocol_mock, \
                mock.patch('rmatics.model.ejudge_run.EjudgeRun.get_test_full_protocol', autospec=True) as get_test_mock:
            fetch_protocol_mock.side_effect = fetch_mock_data
            get_test_mock.side_effect = get_mock_full_protocol
            response = self.call_view()
            assert_that(
                fetch_protocol_mock.call_count,
                equal_to(1)
            )

        assert_that(
            response.json,
            has_entries({
                'tests': has_entries({
                    **tests,
                    '1': 'full 1',
                    '3': 'full 3',
                }),
                'host': host,
                'compiler_output': compiler_output,
            })
        )

    def test_fetch_data_fail(self):
        # При вызове run.fetch_tested_protocol_data может возникнуть какая угодно ошибка, поэтому нужно
        # ее залогировать и выдать пользователю 500
        with mock.patch('rmatics.model.ejudge_run.EjudgeRun.fetch_tested_protocol_data', mock.Mock()) as fetch_protocol_mock:
            fetch_protocol_mock.side_effect = lambda: 1 / 0
            assert_that(
                calling(self.call_view),
                raises(InternalServerError)
            )

    def test_not_found(self):
        assert_that(
            calling(self.call_view).with_args(contest_id=999, run_id=999),
            raises(RunNotFound)
        )

    def test_author_only(self):
        run = EjudgeRun(
            run_id=321,
            contest_id=654,
        )
        db.session.add(run)
        assert_that(
            calling(self.call_view).with_args(
                run_id=run.run_id,
                contest_id=run.contest_id,
            ),
            raises(RunAuthorOnly)
        )


