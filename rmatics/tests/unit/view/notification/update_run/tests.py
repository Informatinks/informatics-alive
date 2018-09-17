import mock
from hamcrest import (
    assert_that,
    calling,
    equal_to,
    has_items,
    raises,
)

from rmatics.model import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.run import Run
from rmatics.testutils import TestCase
from rmatics.utils.exceptions import RunNotFound
from rmatics.view.notification import notification_update_run


class TestView__notification_update_run(TestCase):
    def setUp(self):
        super(TestView__notification_update_run, self).setUp()

        self.create_problems()
        self.create_users()

        self.ej_run = EjudgeRun(
            run_id=123,
            user=self.users[0],
            problem=self.problems[0],
        )
        db.session.add(self.ej_run)
        db.session.flush()

        self.run = Run.from_ejudge_run(self.ej_run)
        db.session.add(self.run)
        db.session.flush()

    def call_view(self, contest_id=None, run_id=None):
        request_args = {}
        if contest_id:
            request_args['contest_id'] = contest_id
        if run_id:
            request_args['run_id'] = run_id

        with self.app.test_request_context(query_string=request_args):
            result = notification_update_run()
        return result

    def test_simple(self):
        sync_mock = mock.Mock(return_value=self.run)
        notify_user_mock = mock.Mock()
        with mock.patch('rmatics.view.notification.Run.sync', sync_mock), \
                mock.patch('rmatics.view.notification.notify_user', notify_user_mock), \
                mock.patch('rmatics.view.notification.Run.source', mock.Mock()):
            self.call_view(contest_id=self.ej_run.contest_id, run_id=self.ej_run.run_id)

        sync_mock.assert_called_once_with(
            ejudge_run_id=self.ej_run.run_id,
            ejudge_contest_id=self.ej_run.contest_id,
        )
        assert_that(
            notify_user_mock.call_args[0][0],
            equal_to(self.users[0].id)
        )
        assert_that(
            notify_user_mock.call_args[0][1],
            equal_to('RUNS_FETCH')
        )
        assert_that(
            notify_user_mock.call_args[0][2],
            has_items('runs')
        )

    def test_run_not_found(self):
        assert_that(
            calling(self.call_view).with_args(contest_id=11, run_id=22),
            raises(RunNotFound),
        )
