import flask_testing
import unittest
import sys

from rmatics import create_app
from rmatics.model import CourseModule
from rmatics.model.base import db, mongo, redis
from rmatics.model.group import (
    Group,
    UserGroup,
)
from rmatics.model.problem import (
    EjudgeProblem,
    Problem)
from rmatics.model.statement import Statement, StatementProblem
from rmatics.model.user import SimpleUser


class TestCase(flask_testing.TestCase):
    CONFIG = {
        'SERVER_NAME': 'localhost',
        'URL_ENCODER_ALPHABET': 'abc',
    }

    def create_app(self):
        app = create_app(config='rmatics.config.TestConfig')
        return app

    def setUp(self):
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        assert mongo.db.name == 'test'
        mongo.db.client.drop_database(mongo.db)

        redis.flushdb()

    def get_session(self):
        with self.client.session_transaction() as session:
            return dict(session)

    def set_session(self, data):
        with self.client.session_transaction() as session:
            session.update(data)

    def create_groups(self):
        self.groups = [
            Group(
                name='group 1',
                visible=1,
            ),
            Group(
                name='group 2',
                visible=1,
            ),
        ]
        db.session.add_all(self.groups)
        db.session.flush(self.groups)

    def create_ejudge_problems(self):
        self.ejudge_problems = [
            EjudgeProblem.create(
                ejudge_prid=1,
                contest_id=1,
                ejudge_contest_id=1,
                problem_id=1,
            ),
            EjudgeProblem.create(
                ejudge_prid=2,
                contest_id=2,
                ejudge_contest_id=1,
                problem_id=2,
            ),
            EjudgeProblem.create(
                ejudge_prid=3,
                contest_id=3,
                ejudge_contest_id=2,
                problem_id=1,
            )
        ]
        db.session.add_all(self.ejudge_problems)
        db.session.flush(self.ejudge_problems)

    def create_problems(self):
        self.problems = [
            Problem(name='Problem1', pr_id=self.ejudge_problems[0].id),
            Problem(name='Problem2', pr_id=self.ejudge_problems[1].id),
            Problem(name='Problem3', pr_id=self.ejudge_problems[2].id),
        ]
        db.session.add_all(self.problems)
        db.session.flush(self.problems)

    def create_statements(self):
        self.statements = [
            Statement(),
            Statement(),
        ]
        db.session.add_all(self.statements)
        db.session.flush(self.statements)

    def create_statement_problems(self):
        self.statement_problems = [
            StatementProblem(problem_id=self.problems[0].id,
                             statement_id=self.statements[0].id,
                             rank=1),
            StatementProblem(problem_id=self.problems[1].id,
                             statement_id=self.statements[0].id,
                             rank=1),
            StatementProblem(problem_id=self.problems[2].id,
                             statement_id=self.statements[0].id,
                             rank=1),
        ]
        db.session.add_all(self.statement_problems)
        db.session.flush(self.statement_problems)

    def create_course_module_statement(self):
        self.course_module_statement = CourseModule(instance_id=self.statements[0].id,
                                                    module=Statement.MODULE)
        db.session.add(self.course_module_statement)
        db.session.flush()

    def create_users(self):
        self.users = [
            SimpleUser(
                firstname='Maxim',
                lastname='Grishkin',
                ejudge_id=179,
            ),
            SimpleUser(
                firstname='Somebody',
                lastname='Oncetoldme',
                ejudge_id=1543,
            ),
            SimpleUser(
                firstname='Anotherone',
                lastname='Oncetoldme',
                ejudge_id=1544,
            ),
        ]
        db.session.add_all(self.users)
        db.session.flush(self.users)


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        path = 'tests'
    else:
        path = sys.argv[1]

    try:
        tests = unittest.TestLoader().discover(path)
    except:
        tests = unittest.TestLoader().loadTestsFromName(path)

    result = unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()
    sys.exit(not result)
