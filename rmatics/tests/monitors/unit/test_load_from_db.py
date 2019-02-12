import datetime

from mock import MagicMock

from rmatics import db
from rmatics import monitor_cacher
from rmatics.model import Run
from rmatics.testutils import TestCase
from rmatics.view.monitors.monitor import MonitorAPIView, get_runs


class TestGenerateMonitor(TestCase):
    def setUp(self):
        super().setUp()

        self.mock_cacher_get = MagicMock(return_value='')
        self.mock_cacher_set = MagicMock()

        monitor_cacher._instance.store.get = self.mock_cacher_get
        monitor_cacher._instance.store.set = self.mock_cacher_set

        self.create_users()
        self.create_statements()
        self.create_ejudge_problems()
        self.create_problems()
        self.create_statement_problems()
        self.create_course_module()
        self.create_runs()

        db.session.commit()

        self.contest_id = self.course_module.id

    def create_runs(self, creation_time=None):
        if not hasattr(self, 'runs'):
            self.runs = []
        runs = [
            Run(problem_id=self.problems[0].id,
                user_id=self.users[0].id),
            Run(problem_id=self.problems[0].id,
                user_id=self.users[1].id),
            Run(problem_id=self.problems[0].id,
                user_id=self.users[2].id),
        ]

        if creation_time is not None:
            for run in runs:
                run.create_time = creation_time

        self.runs += runs

        db.session.add_all(runs)
        db.session.commit()

    def test_get_ejudge_problems(self):
        problems = MonitorAPIView._get_problems(self.contest_id)

        expected_ids = sorted(map(lambda p: p.id, self.problems))

        ids = sorted(map(lambda p: p.id, problems))

        self.assertEqual(ids, expected_ids)

    def test_get_runs(self):
        user_ids = [user.id for user in self.users]
        runs = get_runs(problem_id=self.problems[0].id,
                        user_ids=user_ids)

        self.assertEqual(len(runs), 3)

        self.mock_cacher_get.assert_called_once()
        self.mock_cacher_set.assert_called_once()

    def test_get_runs_before(self):
        time_creation = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        time_before = time_creation - datetime.timedelta(hours=1)
        self.create_runs(time_creation)

        user_ids = [user.id for user in self.users]
        runs = get_runs(problem_id=self.problems[0].id,
                        user_ids=user_ids,
                        time_before=int(time_before.timestamp()))

        self.assertEqual(len(runs), 3)

    def test_get_runs_after(self):
        time_creation = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        self.create_runs(time_creation)
        time_after = time_creation + datetime.timedelta(hours=1)

        user_ids = [user.id for user in self.users]
        runs = get_runs(problem_id=self.problems[0].id,
                        user_ids=user_ids,
                        time_after=int(time_after.timestamp()))

        self.assertEqual(len(runs), 3)

    def test_get_runs_before_and_after(self):
        time_creation = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        self.create_runs(time_creation)
        time_after = time_creation + datetime.timedelta(hours=1)

        time_creation = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        self.create_runs(time_creation)
        time_before = time_creation - datetime.timedelta(hours=1)

        user_ids = [user.id for user in self.users]
        runs = get_runs(problem_id=self.problems[0].id,
                        user_ids=user_ids,
                        time_after=int(time_after.timestamp()),
                        time_before=int(time_before.timestamp()))

        self.assertEqual(len(runs), 3)
