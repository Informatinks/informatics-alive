import json

import mock
from flask import g, url_for
from hamcrest import (
    assert_that,
    contains_inanyorder
)

from rmatics.model.base import db
from rmatics.model.run import Run
from rmatics.testutils import TestCase
from rmatics.utils.run import EjudgeStatusesEnum
from rmatics.view.problem.problem import problem_runs


class TestView__problem_runs(TestCase):
    def setUp(self):
        super(TestView__problem_runs, self).setUp()

        self.create_problems()
        self.create_statements()
        self.create_users()

        self.user1 = self.users[0]
        self.user2 = self.users[1]
        self.problem = self.problems[0]

        self.runs = [
            [
                Run(
                    problem=self.problem,
                    user=user
                )
                for i in range(3)
            ]
            for user in [self.user1, self.user2]
        ]
        db.session.add_all(self.runs[0])  # user1 runs
        db.session.add_all(self.runs[1])  # user2 runs
        db.session.flush()

    def test_filters_by_user_id(self):
        with mock.patch('rmatics.model.run.Run.serialize', autospec=True) as serialize_mock:
            serialize_mock.side_effect = lambda self, *args: 'serialized'
            with self.app.test_request_context():
                g.user = self.user1
                response = problem_runs(self.problem.id)

        assert_that(
            response.json.keys(),
            contains_inanyorder(
                *[str(run.id) for run in self.runs[0]]
            )
        )

    def test_filter_by_statement_id(self):
        # Для двух посылок их трех у каждого пользователя задаем statement_id
        for i in range(2):
            for (statement, run) in zip(self.statements, self.runs[i]):
                run.statement = statement

        with mock.patch('rmatics.model.run.Run.serialize', autospec=True) as serialize_mock, \
                mock.patch('rmatics.model.run.Run.source', mock.Mock(return_value='')):
            serialize_mock.side_effect = lambda self, *args: 'serialized'
            with self.app.test_request_context(query_string={'statement_id': self.statements[0].id}):
                g.user = self.user1
                response = problem_runs(self.problems[0].id)

        assert_that(
            response.json.keys(),
            contains_inanyorder(
                str(self.runs[0][0].id),
                str(self.runs[1][0].id),
            )
        )


class TestUpdateRun(TestCase):
    def setUp(self):
        super().setUp()

        self.create_users()
        self.create_statements()
        self.create_problems()

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)

        self.run = Run(
            user_id=self.users[0].id,
            problem=self.problems[0],
            problem_id=self.problems[0].id,
            statement_id=self.statements[0].id,
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=1,
            ejudge_status=EjudgeStatusesEnum.COMPILING,
            source_hash=source_hash,
        )
        db.session.add(self.run)
        db.session.commit()

    def send_request(self, run_id, data):
        url = url_for('problem.run', run_id=run_id)
        data = json.dumps(data)
        resp = self.client.put(url, data=data)
        return resp

    def test_simple(self):
        data = {
            'ejudge_status': 100500
        }

        resp = self.send_request(self.run.id, data)

        self.assert200(resp)

        data = resp.json

        self.assertIn('data', data)
        data = data['data']

        self.assertIn('id', data)
        self.assertIn('ejudge_status', data)
        self.assertIn('ejudge_test_num', data)
        self.assertIn('ejudge_score', data)

        self.assertEqual(data['ejudge_status'], 100500)

        db.session.refresh(self.run)

        self.assertEqual(self.run.ejudge_status, 100500)
