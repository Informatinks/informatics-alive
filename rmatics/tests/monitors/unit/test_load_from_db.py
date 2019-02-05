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

    def test_get_ejudge_problems(self):
        problems = MonitorAPIView._get_ejudge_problems(self.contest_id)

        expected_pr_ids = sorted(map(lambda p: p.pr_id, self.problems))

        pr_ids = sorted(map(lambda p: p.pr_id, problems))

        self.assertEqual(pr_ids, expected_pr_ids)

    def test_get_runs(self):
        user_ids = [user.id for user in self.users]
        runs = get_runs(problem_id=self.problems[0].id,
                        user_ids=user_ids)

        self.assertEqual(len(runs), 3)

        self.mock_cacher_get.assert_called_once()
        self.mock_cacher_set.assert_called_once()
