import flask_testing
import unittest
import sys

from rmatics import create_app
from rmatics.model import (
    db,
    mongo,
    redis,
)
from rmatics.model.group import (
    Group,
    UserGroup,
)
from rmatics.model.problem import (
    EjudgeProblem,
)
from rmatics.model.role import Role
from rmatics.model.statement import Statement
from rmatics.model.user import SimpleUser


class TestCase(flask_testing.TestCase):
    CONFIG = {
        'SERVER_NAME': 'localhost',
        'URL_ENCODER_ALPHABET': 'abc',
    }

    def create_app(self):
        app = create_app(config=self.CONFIG)
        return app

    def setUp(self):
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

    def create_problems(self):
        self.problems = [
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
        db.session.add_all(self.problems)
        db.session.flush(self.problems)

    def create_roles(self):
        self.admin_role = Role(shortname='admin')
        db.session.add_all((self.admin_role,))

    def create_statements(self):
        self.statements = [
            Statement(),
            Statement(),
        ]
        db.session.add_all(self.statements)
        db.session.flush(self.statements)

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
        ]
        db.session.add_all(self.users)
        db.session.flush(self.users)

    def create_user_groups(self):
        self.create_groups()
        self.create_users()

        self.user_groups = [
            UserGroup(
                group=self.groups[0],
                user=self.users[0],
            ),
            UserGroup(
                group=self.groups[1],
                user=self.users[1],
            ),
        ]
        db.session.add_all(self.user_groups)
        db.session.flush(self.user_groups)


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

