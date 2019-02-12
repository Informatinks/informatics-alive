import datetime

from flask import url_for
from mock import MagicMock

from rmatics import db, monitor_cacher
from rmatics.model import Run, UserGroup
from rmatics.testutils import TestCase


class TestMonitorGetApi(TestCase):
    def setUp(self):
        super().setUp()

        self.mock_cacher_get = MagicMock(return_value='')
        self.mock_cacher_set = MagicMock()

        monitor_cacher._instance.store.get = self.mock_cacher_get
        monitor_cacher._instance.store.set = self.mock_cacher_set

        self.create_users()
        self.create_groups()

        for user in self.users:
            ug = UserGroup(user_id=user.id, group_id=self.groups[0].id)
            db.session.add(ug)

        self.create_statements()
        self.create_ejudge_problems()
        self.create_problems()
        self.create_statement_problems()
        self.create_course_module()
        self.create_runs()

        db.session.commit()

        self.contest_id = self.course_module.id

    def create_runs(self):
        self.runs = [
            Run(problem_id=self.problems[0].id,
                user_id=self.users[0].id),
            Run(problem_id=self.problems[0].id,
                user_id=self.users[1].id),
            Run(problem_id=self.problems[0].id,
                user_id=self.users[2].id),
        ]
        db.session.add_all(self.runs)

    def send_request(self, **data):
        url = url_for('monitor.crud', **data)
        resp = self.client.get(url)
        return resp

    def test_simple(self):
        # Run-ы созданы в utcnow()
        time_after = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        time_before = datetime.datetime.utcnow() + datetime.timedelta(days=1)

        resp = self.send_request(contest_id=self.contest_id, group_id=self.groups[0].id,
                                 time_after=int(time_after.timestamp()),
                                 time_before=int(time_before.timestamp()),)
        self.assert200(resp)

        self.assertEqual(self.mock_cacher_get.call_count, 3)
        self.assertEqual(self.mock_cacher_set.call_count, 3)

        self.assertIn('data', resp.json)
        data = resp.json['data']

        self.assertEqual(len(data), 3)

        for contest_data in data:
            self.assertIn('problem', contest_data)
            self.assertIn('runs', contest_data)
            self.assertIn('contest_id', contest_data)

        problem_data = data[0]['problem']
        self.assertIn('rank', problem_data)

        runs = map(lambda d: d['runs'], data)
        runs_lens = map(len, runs)

        self.assertEqual(sum(runs_lens), 3)
