# import mock
# from hamcrest import (
#     assert_that,
#     calling,
#     raises,
# )

# from pynformatics.testutils import TestCase
# from pynformatics.utils.context import Context
# from pynformatics.utils.exceptions import Forbidden
# from pynformatics.view.problem import problem_submits_v2


# class TestView__problem_submits_v2(TestCase):
#     def setUp(self):
#         super(TestView__problem_submits_v2, self).setUp()

#         self.ejudge_submit_patcher = mock.patch('pynformatics.view.problem.submit', mock.Mock())
#         self.ejudge_submit_patcher.start()

#         self.check_auth_patcher = mock.patch.object(Context, 'check_auth', mock.Mock())
#         self.check_auth_patcher.start()

#         self.request.registry.settings['ejudge.new_client_url'] = ''
#         self.request.POST = {'file': mock.Mock()}

#         self.get_languages_patcher = mock.patch.object(Context, 'get_allowed_languages')
#         self.get_languages_mock = self.get_languages_patcher.start()

#     def tearDown(self):
#         super(TestView__problem_submits_v2, self).tearDown()
#         self.ejudge_submit_patcher.stop()
#         self.check_auth_patcher.stop()
#         self.get_languages_patcher.stop()

#     def test_not_allowed_language(self):
#         """
#         Tries to submit problem with not allowed language id. Must raise 403 Forbidden
#         """
#         allowed_languages = ['1', '2']
#         lang_id = '3'
#         self.get_languages_mock.return_value = allowed_languages
#         self.request.params = {'lang_id': lang_id, 'file': mock.Mock()}

#         assert_that(
#             calling(problem_submits_v2).with_args(self.request),
#             raises(Forbidden),
#         )
import io
from io import BytesIO

from unittest.mock import patch, MagicMock

from flask import url_for

from rmatics.model.base import db
from rmatics.model.role import RoleAssignment
from rmatics.model.run import Run
from rmatics.testutils import TestCase
from rmatics.view.problem.problem import SubmitApi


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
            ejudge_status=98,  # compiling
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
            ejudge_status=98,  # compiling
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
            ejudge_status=98,  # compiling
            source_hash=source_hash,
        )
        db.session.add(self.run)
        db.session.commit()

        self.run.update_source(blob)

    def send_request(self, run_id):
        url = url_for('problem.run_source', run_id=run_id)
        response = self.client.get(url)
        return response

    def test_simple(self):
        self.set_session({'user_id': self.users[0].id})

        resp = self.send_request(run_id=self.run.id)
        self.assert200(resp)

    def test_wrong_permissions(self):
        self.set_session({'user_id': self.users[1].id})

        resp = self.send_request(run_id=self.run.id)
        self.assert403(resp)

    def test_super_permissions(self):

        role_assignment = RoleAssignment(user_id=self.users[1].id, role=self.admin_role)

        db.session.add(role_assignment)
        db.session.commit()

        self.set_session({'user_id': self.users[1].id})

        resp = self.send_request(run_id=self.run.id)
        self.assert200(resp)
