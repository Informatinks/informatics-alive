import mock

from rmatics import db
from rmatics.ejudge.submit_queue.submit import Submit
from rmatics.ejudge.submit_queue.worker import SubmitWorker
from rmatics.testutils import TestCase
from rmatics.utils.run import EjudgeStatuses

USER_ID = -1
EJUDGE_URL = 'ejudge-url'

EJUDGE_RESPONSE_CODE = 105
EJUDGE_RESPONSE_MESSAGE = 'Error submitting source'
EJUDGE_RESPONSE = {
    'code': EJUDGE_RESPONSE_CODE,
    'message': EJUDGE_RESPONSE_MESSAGE
}


class TestEjudge__submit_queue_submit_worker_handle_submit(TestCase):
    def setUp(self):
        super(TestEjudge__submit_queue_submit_worker_handle_submit, self).setUp()
        self.create_users()
        self.create_ejudge_problems()
        self.create_runs()

        self.submit_mock = mock.Mock()
        self.queue_mock = mock.Mock()
        self.queue_mock.get.return_value = self.submit_mock

    def test_successful(self):
        worker = SubmitWorker(self.queue_mock)
        worker.handle_submit()

        self.queue_mock.get.assert_called_once()
        self.submit_mock.send.assert_called_once()

    def test_failed(self):
        self.submit_mock.send.side_effect = lambda **__: 1 / 0

        worker = SubmitWorker(self.queue_mock)
        worker.handle_submit()

        self.queue_mock.get.assert_called_once()
        self.submit_mock.send.assert_called_once()

    @mock.patch('rmatics.ejudge.submit_queue.submit.db.session.expunge')
    def test_invalid_submit_sets_error_status(self, session_expunge):
        with mock.patch('rmatics.ejudge.submit_queue.submit.submit') as submit_method:
            submit_method.return_value = EJUDGE_RESPONSE
            run = self.runs[0]

            # load associated problems into session
            db.session.add(run)
            db.session.commit()

            submit = Submit(id=None, user_id=USER_ID, run_id=run.id, ejudge_url=EJUDGE_URL)
            submit._get_run = mock.MagicMock()
            submit._get_run.return_value = run

            submit.send()

            submit_method.assert_called_once()

            db.session.refresh(run)
            assert run.ejudge_status == EjudgeStatuses.RMATICS_SUBMIT_ERROR.value

    @mock.patch('rmatics.ejudge.submit_queue.submit.db.session.expunge')
    @mock.patch('rmatics.ejudge.submit_queue.submit.submit')
    def test_invalid_submit_preserves_mongo_protocol(self, submit_method, session_expunge):
            submit_method.return_value = EJUDGE_RESPONSE
            run = self.runs[0]

            # load associated problems into session
            db.session.add(run)
            db.session.commit()

            submit = Submit(id=None, user_id=USER_ID, run_id=run.id, ejudge_url=EJUDGE_URL)
            submit._get_run = mock.MagicMock()
            submit._get_run.return_value = run

            submit.send()

            submit_method.assert_called_once()

            db.session.refresh(run)
            assert run.protocol['run_id'] == run.id
            assert run.protocol['compiler_output'] == EJUDGE_RESPONSE_MESSAGE
