import datetime
import io
import json
from io import BytesIO

from unittest.mock import patch, MagicMock

from bson import ObjectId
from flask import url_for

from rmatics.model.base import db, mongo
from rmatics.model.role import RoleAssignment
from rmatics.model.run import Run
from rmatics.testutils import TestCase
from rmatics.utils.run import EjudgeStatuses
from rmatics.view.problem.problem import SubmitApi

PROTOCOL_ID = ObjectId("507f1f77bcf86cd799439011")
WRONG_PROTOCOL_ID = ObjectId("507f1f77bcf86cd799439012")


class TestCheckFileRestriction(TestCase):
    def setUp(self):
        super().setUp()

    def test_file_too_large(self):
        files = io.BytesIO(bytes((ascii('f') * 64 * 1024).encode('ascii')))
        with self.assertRaises(ValueError):
            SubmitApi.check_file_restriction(files)

        files = io.BytesIO(bytes((ascii('f') * 1).encode('ascii')))

        with self.assertRaises(ValueError):
            SubmitApi.check_file_restriction(files)


class TestTrustedProblemSubmit(TestCase):
    def setUp(self):
        super().setUp()
        self.create_problems()
        self.create_users()
        self.create_statements()

    def send_request(self, problem_id, **kwargs):
        url = url_for('problem.trusted_submit', problem_id=problem_id)
        data = {
            'lang_id': 1,
            'statement_id': self.statements[0].id,
            'user_id': self.users[0].id,
            **kwargs
        }
        response = self.client.post(url, data=data, content_type='multipart/form-data')
        return response

    @patch('rmatics.view.problem.problem.Run.update_source')
    @patch('rmatics.view.problem.problem.queue_submit')
    def test_simple(self, mock_submit, mock_update):
        submit = MagicMock()
        submit.serialize.return_value = {'hhh': 'mmm'}
        mock_submit.return_value = submit

        file = BytesIO(b'skdjvndfkjnvfk')
        data = dict(
            file=(file, 'test.123', )
        )
        resp = self.send_request(self.problems[0].id, **data)

        self.assert200(resp)
        submit.serialize.assert_called_once()
        mock_update.assert_called_once()

    @patch('rmatics.view.problem.problem.Run.update_source')
    @patch('rmatics.view.problem.problem.queue_submit')
    def test_duplicate(self, mock_submit, mock_update):
        submit = MagicMock()
        submit.serialize.return_value = {'hhh': 'mmm'}
        mock_submit.return_value = submit

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)

        run = Run(
            user_id=self.users[0].id,
            problem=self.problems[0],
            problem_id=self.problems[0].id,
            statement_id=self.statements[0].id,
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=1,
            ejudge_status=EjudgeStatuses.COMPILING.value,
            source_hash=source_hash,
        )
        db.session.add(run)
        db.session.commit()

        file = BytesIO(blob)
        data = dict(
            file=(file, 'test.123', )
        )
        resp = self.send_request(self.problems[0].id, **data)

        self.assert400(resp)


class TestProblemSubmit(TestCase):

    def setUp(self):
        super().setUp()
        self.create_problems()
        self.create_users()
        self.create_statements()

        self.set_session({'user_id': self.users[0].id})

    def send_request(self, problem_id, **kwargs):
        url = url_for('problem.submit', problem_id=problem_id)
        data = {
            'lang_id': 1,
            'statement_id': self.statements[0].id,
            'user_id': self.users[0].id,
            **kwargs
        }
        response = self.client.post(url, data=data, content_type='multipart/form-data')
        return response

    @patch('rmatics.view.problem.problem.Run.update_source')
    @patch('rmatics.view.problem.problem.queue_submit')
    def test_simple(self, mock_submit, mock_update):
        submit = MagicMock()
        submit.serialize.return_value = {'hhh': 'mmm'}
        mock_submit.return_value = submit

        file = BytesIO(b'skdjvndfkjnvfk')
        data = dict(
            file=(file, 'test.123', )
        )
        resp = self.send_request(self.problems[0].id, **data)

        self.assert200(resp)
        submit.serialize.assert_called_once()
        mock_update.assert_called_once()

    @patch('rmatics.view.problem.problem.Run.update_source')
    @patch('rmatics.view.problem.problem.queue_submit')
    def test_duplicate(self, mock_submit, mock_update):
        submit = MagicMock()
        submit.serialize.return_value = {'hhh': 'mmm'}
        mock_submit.return_value = submit

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)

        run = Run(
            user_id=self.users[0].id,
            problem=self.problems[0],
            problem_id=self.problems[0].id,
            statement_id=self.statements[0].id,
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=1,
            ejudge_status=EjudgeStatuses.COMPILING.value,
            source_hash=source_hash,
        )
        db.session.add(run)
        db.session.commit()

        file = BytesIO(blob)
        data = dict(
            file=(file, 'test.123', )
        )
        resp = self.send_request(self.problems[0].id, **data)

        self.assert400(resp)


class TestGetSubmissionSource(TestCase):
    def setUp(self):
        super().setUp()

        self.create_roles()

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
            ejudge_status=EjudgeStatuses.COMPILING.value,
            source_hash=source_hash,
        )
        db.session.add(self.run)
        db.session.commit()

        self.run.update_source(blob)

    def send_request(self, run_id, data=None):
        data = data or {}
        url = url_for('problem.run_source', run_id=run_id, **data)
        response = self.client.get(url)
        return response

    def test_simple(self):
        data = {'user_id': self.users[0].id}

        resp = self.send_request(run_id=self.run.id, data=data)
        self.assert200(resp)

    # TODO: revrite test (NFRMTCS-26)
    def test_wrong_permissions(self):
        data = {'user_id': self.users[1].id}

        resp = self.send_request(run_id=self.run.id, data=data)
        self.assert404(resp)

    def test_super_permissions(self):
        data = {'is_admin': True}

        resp = self.send_request(run_id=self.run.id, data=data)
        self.assert200(resp)


class TestUpdateSubmissionFromEjudge(TestCase):
    def setUp(self):
        super().setUp()

        self.create_roles()
        self.create_users()
        self.create_problems()

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)

        self.run = Run(
            user_id=self.users[0].id,
            problem=self.problems[0],
            problem_id=self.problems[0].id,
            statement_id=None,
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=1,
            ejudge_status=EjudgeStatuses.COMPILING.value,
            source_hash=source_hash,
            ejudge_run_id=1
        )
        db.session.add(self.run)
        db.session.commit()

    def send_request_to_update_run(self, **data):
        data = json.dumps(data)
        url = url_for('problem.update_from_ejudge')
        resp = self.client.post(url, data=data)
        return resp

    def test_simple(self):
        run_data = {
            'run_uuid': 'uuid',
            'score': 15,
            'status': 37,
            'lang_id': 2,
            'test_num': 123,
            'create_time':  datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
            'last_change_time': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
        }

        request_data = {
            'run_id': self.run.ejudge_run_id,
            'contest_id': self.run.ejudge_contest_id,
            **run_data,
        }

        resp = self.send_request_to_update_run(**request_data)

        self.assert200(resp)

        db.session.refresh(self.run)

        # Не проверяем поля с датой
        run_data.pop('create_time')
        run_data.pop('last_change_time')

        for k, v in run_data.items():
            run_attr = getattr(self.run, f'ejudge_{k}')
            self.assertEqual(run_attr, v)

    def test_update_mongo(self):
        run_data = {
            'run_uuid': 'uuid',
            'score': 15,
            'status': 37,
            'lang_id': 2,
            'test_num': 123,
            'create_time': datetime.datetime.now().isoformat(),
            'last_change_time': datetime.datetime.now().isoformat(),
        }

        protocol_id = PROTOCOL_ID

        mongo.db.protocol.insert_one({'_id': protocol_id})

        request_data = {
            'run_id': self.run.ejudge_run_id,
            'contest_id': self.run.ejudge_contest_id,
            'mongo_protocol_id': protocol_id,
            **run_data,
        }

        resp = self.send_request_to_update_run(**request_data)

        self.assert200(resp)

        data = mongo.db.protocol.find_one({'_id': self.run.id})
        self.assertIsNotNone(data)

    def test_bad_mongo_id(self):
        run_data = {
            'run_uuid': 'uuid',
            'score': 15,
            'status': 37,
            'lang_id': 2,
            'test_num': 123,
            'create_time': datetime.datetime.now().isoformat(),
            'last_change_time': datetime.datetime.now().isoformat(),
        }

        protocol_id = WRONG_PROTOCOL_ID

        request_data = {
            'run_id': self.run.ejudge_run_id,
            'contest_id': self.run.ejudge_contest_id,
            'mongo_protocol_uuid': protocol_id,
            **run_data,
        }

        resp = self.send_request_to_update_run(**request_data)

        self.assert400(resp)


class TestGetRunProtocol(TestCase):
    def setUp(self):
        super().setUp()

        self.create_roles()
        self.create_users()
        self.create_problems()

        blob = b'skdjvndfkjnvfk'

        source_hash = Run.generate_source_hash(blob)

        self.run = Run(
            user_id=self.users[0].id,
            problem=self.problems[0],
            problem_id=self.problems[0].id,
            statement_id=None,
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=1,
            ejudge_status=EjudgeStatuses.COMPILING.value,
            source_hash=source_hash,
            ejudge_run_id=1
        )
        db.session.add(self.run)
        db.session.commit()

    def send_request(self):
        url = url_for('problem.run_protocol', run_id=self.run.id)
        resp = self.client.get(url)
        return resp

    def test_not_found(self):
        resp = self.send_request()
        self.assert404(resp)

    def test_simple(self):
        report = b'blob'
        mongo.db.protocol.insert_one({'protocol_id': self.run.id,
                                      'blob': report})
        resp = self.send_request()
        self.assert200(resp)
