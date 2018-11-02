from datetime import datetime, timedelta

from flask import url_for

from rmatics.model import db
from rmatics.model.problem import Problem
from rmatics.model.run import Run
from rmatics.model.user import SimpleUser
from rmatics.testutils import TestCase


class TestAPIProblemSubmission(TestCase):
    def setUp(self):
        super().setUp()

        self.problem1 = Problem(name='Problem1')
        self.problem2 = Problem(name='Problem2')

        db.session.add_all([self.problem1, self.problem2])

        self.user1 = SimpleUser(firstname='user1', lastname='user1')
        self.user2 = SimpleUser(firstname='user2', lastname='user2')

        db.session.add_all([self.user1, self.user2])

        db.session.flush()

        self.run1 = Run(user_id=self.user1.id, problem_id=self.problem1.id,
                        ejudge_status=1, ejudge_language_id=1)
        self.run2 = Run(user_id=self.user1.id, problem_id=self.problem2.id,
                        ejudge_status=1, ejudge_language_id=1)
        self.run3 = Run(user_id=self.user2.id, problem_id=self.problem1.id,
                        ejudge_status=2, ejudge_language_id=2)
        self.run4 = Run(user_id=self.user2.id, problem_id=self.problem2.id,
                        ejudge_status=2, ejudge_language_id=2)

        self.run4.create_time = datetime.utcnow() - timedelta(days=1)

        db.session.add_all([self.run1, self.run2, self.run3, self.run4])

        db.session.commit()

    def send_request(self, problem_id: int, **kwargs):
        route = url_for('problem.problem_submissions', problem_id=problem_id)

        data = {
            'page': 1,
            **kwargs
        }

        response = self.client.get(route, data=data)
        return response

    def test_simple(self):
        resp = self.send_request(self.problem1.id)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 2)

        self.assertIn('metadata', data)

        self.assertIn('count', data['metadata'])
        self.assertEqual(data['metadata']['count'], 2)

        self.assertIn('page_count', data['metadata'])
        self.assertEqual(data['metadata']['page_count'], 1)

        run0 = data['data'][0]

        # Common fields
        self.assertIn('id', run0)
        self.assertIsNotNone(run0['id'])

        self.assertIn('user', run0)
        self.assertIsNotNone(run0['user'])

        self.assertIn('problem', run0)
        self.assertIsNotNone(run0['problem'])

        self.assertIn('ejudge_status', run0)
        self.assertIsNotNone(run0['ejudge_status'])

        self.assertIn('create_time', run0)
        self.assertIsNotNone(run0['create_time'])

        # User
        user = run0['user']
        self.assertIn('id', user)
        self.assertIsNotNone(user['id'])

        self.assertIn('firstname', user)
        self.assertIsNotNone(user['firstname'])

        self.assertIn('lastname', user)
        self.assertIsNotNone(user['lastname'])

        # Problem
        problem = run0['problem']
        self.assertIn('name', problem)
        self.assertIsNotNone(problem['name'])

    def test_filter_by_user(self):
        resp = self.send_request(self.problem1.id, user_id=self.user1.id)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 1)

    def test_filter_by_lang(self):
        resp = self.send_request(self.problem1.id, lang_id=self.run1.ejudge_language_id)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 1)

    def test_filter_by_status(self):
        resp = self.send_request(self.problem1.id, status_id=self.run1.ejudge_status)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 1)

    def test_filter_by_statement(self):
        resp = self.send_request(self.problem1.id, status_id=self.run1.statement_id)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 2)

    def test_filter_by_from_timestamp(self):

        from_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)

        resp = self.send_request(self.problem2.id, from_timestamp=from_time)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 1)

        # Too mush for timestamp
        resp = self.send_request(self.problem2.id, from_timestamp=from_time * 10000)
        self.assert400(resp)

    def test_filter_by_to_timestamp(self):

        to_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)

        resp = self.send_request(self.problem2.id, to_timestamp=to_time)

        self.assert200(resp)

        data = resp.get_json()
        self.assertEqual(data['result'], 'success')
        self.assertEqual(len(data['data']), 1)

        # Too mush for timestamp
        resp = self.send_request(self.problem2.id, to_timestamp=to_time * 10000)
        self.assert400(resp)