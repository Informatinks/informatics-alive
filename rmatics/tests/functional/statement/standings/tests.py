import datetime
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
)

from rmatics.model.base import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.pynformatics_run import PynformaticsRun
from rmatics.model.statement import Statement
from rmatics.testutils import TestCase


class TestAPI__statement_standings(TestCase):
    def setUp(self):
        super(TestAPI__statement_standings, self).setUp()

        self.create_user_groups()
        self.create_problems()

        self.statement = Statement()
        db.session.add(self.statement)
        db.session.flush()

    def send_request(self, group_id=None):
        query_string = {}
        if group_id:
            query_string['group_id'] = group_id
        response = self.client.get(
            '/statement/1/standings',
            query_string=query_string,
        )
        return response

    def test_simple(self):
        runs = [
            EjudgeRun(
                run_id=1,
                contest_id=1,
                problem=self.problems[0],
                user=self.users[0],
                create_time=datetime.datetime(2018, 2, 23, 23, 3, 5),
                score=100,
                status=0,
            ),
        ]
        db.session.add_all(runs)

        pynformatics_runs = [
            PynformaticsRun(run=runs[0], statement_id=1)
        ]
        db.session.add_all(pynformatics_runs)

        response = self.send_request()
        assert_that(response.status_code, equal_to(200))
        assert_that(
            response.json,
            equal_to({
                '1': {
                    'firstname': 'Maxim',
                    'lastname': 'Grishkin',
                    'runs': [
                        {
                            'run_id': 1,
                            'contest_id': 1,
                            'create_time': '2018-02-23T23:03:05',
                            'score': 100,
                            'status': 0,
                            'problem_id': 1,
                        }
                    ]
                }
            })
        )

    def test_does_not_creates_twice(self):
        # Ошибку кинет база данных при попытке создать объект с неуникальным ключом
        self.send_request()
        self.send_request()

    def test_filter_by_group_id(self):
        runs = [
            EjudgeRun(
                run_id=1,
                contest_id=1,
                problem=self.problems[0],
                user=self.users[0],
                create_time=datetime.datetime(2018, 2, 23, 23, 3, 5),
                score=100,
                status=0,
            ),
            EjudgeRun(
                run_id=2,
                contest_id=1,
                problem=self.problems[0],
                user=self.users[1],
                create_time=datetime.datetime(2018, 2, 23, 23, 3, 5),
                score=100,
                status=0,
            ),
        ]
        db.session.add_all(runs)

        pynformatics_runs = [
            PynformaticsRun(run=runs[0], statement_id=1),
            PynformaticsRun(run=runs[1], statement_id=1)
        ]
        db.session.add_all(pynformatics_runs)

        response_not_filtered = self.send_request()
        assert_that(response_not_filtered.status_code, equal_to(200))

        response_filtered = self.send_request(group_id=1)
        assert_that(response_filtered.status_code, equal_to(200))

        assert_that(
            response_not_filtered.json.keys(),
            contains_inanyorder('1', '2')
        )
        assert_that(
            response_filtered.json.keys(),
            contains_inanyorder('1')
        )
