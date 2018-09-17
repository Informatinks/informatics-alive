import mock
from flask import g
from hamcrest import (
    assert_that,
    has_entries,
)

from rmatics.model import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.role import RoleAssignment
from rmatics.testutils import TestCase
from rmatics.view.protocol import protocol_get_full


class TestView__protocol_get_full(TestCase):
    def setUp(self):
        super(TestView__protocol_get_full, self).setUp()

        self.create_users()
        self.create_roles()

        role_assignment = RoleAssignment(
            user_id=self.users[0].id,
            role=self.admin_role,
        )
        db.session.add(role_assignment)
        db.session.flush()

        self.contest_id = 1234
        self.run_id = 5678
        # self.request.matchdict = {
        #     'contest_id': self.contest_id,
        #     'run_id': self.run_id
        # }

    def _get_mocked_run(self,
                        count,
                        status_string,
                        ):
        """
        Создает замоканый run
        """
        run = mock.Mock()
        run.user.statement.filter = lambda *args: run.user.statement
        run.user.statement.count = lambda *args: count
        run.status_string = status_string
        run.host = ''
        run.get_audit = lambda: ''
        run.tests = {}
        return run

    def test_compilation_error(self):
        run = self._get_mocked_run(count=0, status_string='CE')
        compiler_output = 'mocked compiler output'
        run.compiler_output = compiler_output

        with mock.patch.object(EjudgeRun, 'get_by', mock.Mock(return_value=run)):
            with self.app.test_request_context():
                g.user = self.users[0]
                response = protocol_get_full(contest_id=self.contest_id, run_id=self.run_id)

        assert_that(
            response.json,
            has_entries({
                'compiler_output': compiler_output,
            })
        )
