import datetime

import mock
import sys
from hamcrest import (
    assert_that,
    anything,
    calling,
    equal_to,
    is_not,
    raises,
)

from rmatics.model.base import db
from rmatics.model.run import Run
from rmatics.model.ejudge_run import EjudgeRun, EjudgeStatusesEnum
from rmatics.testutils import TestCase


if 'rmatics.ejudge.submit_queue.submit' in sys.modules:
    del sys.modules['rmatics.ejudge.submit_queue.submit']
with mock.patch('rmatics.ejudge.ejudge_proxy.submit') as ejudge_submit_mock, \
        mock.patch('rmatics.websocket.notify_user') as notify_user_mock:
    from rmatics.ejudge.submit_queue.submit import Submit


class TestEjudge__submit_queue_submit_send(TestCase):
    def setUp(self):
        super(TestEjudge__submit_queue_submit_send, self).setUp()

        ejudge_submit_mock.reset_mock()
        notify_user_mock.reset_mock()

        self.create_users()
        self.create_problems()
        self.create_statements()

        self.run = EjudgeRun(
            run_id=12,
            user=self.users[0],
            problem=self.problems[0],
        )
        db.session.add(self.run)
        db.session.flush([self.run])

        self.file_mock = mock.Mock()
        # self.file_mock.value.decode.return_value = 'source'
        self.file_mock.filename = 'filename'
        self.file_mock.read.return_value = b'source'

    def test_simple(self):
        run = Run(
            user_id=self.users[0].id,
            problem_id=self.problems[0].id,
            statement_id=self.statements[0].id,
            create_time=datetime.datetime(2018, 3, 30, 16, 59, 0),
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=27,
            ejudge_status=EjudgeStatusesEnum.COMPILING,
        )
        db.session.add(run)
        db.session.flush()
        db.session.refresh(run)

        file = self.file_mock

        text = file.read()
        run.update_source(text)

        submit = Submit(
            id=1,
            user_id=self.users[0].id,
            run_id=run.id,
            ejudge_url='ejudge_url',
        )

        ejudge_submit_mock.return_value = {
            'code': 0,
            'run_id': self.run.run_id,
        }

        submit.send()

        from flask import current_app

        ejudge_submit_mock.assert_called_once_with(
            run_file=b'source',
            contest_id=1,
            prob_id=1,
            lang_id=27,
            login=current_app.config['EJUDGE_USER'],
            password=current_app.config['EJUDGE_PASSWORD'],
            filename='common_filename',
            url='ejudge_url',
            user_id=1,
        )

        run = db.session.query(Run).one()
        assert_that(run.ejudge_run_id, equal_to(self.run.run_id))
        assert_that(run.ejudge_contest_id, equal_to(self.problems[0].ejudge_contest_id))
        assert_that(run.user.id, equal_to(self.users[0].id))
        assert_that(run.problem.id, equal_to(self.problems[0].id))

        notify_user_mock.assert_called_once_with(
            1,
            'SUBMIT_SUCCESS',
            {
               'run': {
                    'id': 1,
                    'create_time': '2018-03-30 16:59:00',
                    'ejudge_run_id': 12,
                    'ejudge_contest_id': 1,
                    'language_id': 27,
                    'problem_id': 1,
                    'statement_id': 1,
                    'score': None,
                    'status': 98,
                    'user': {
                        'id': 1,
                        'firstname': 'Maxim',
                        'lastname': 'Grishkin',
                        'ejudge_id': 179,
                    },
                },
                'submit_id': 1,
            }
        )

    def test_handles_submit_exception(self):
        # В случае, если функция submit бросила исключение
        run = Run(
            user_id=self.users[0].id,
            problem_id=self.problems[0].id,
            statement_id=self.statements[0].id,
            create_time=datetime.datetime(2018, 3, 30, 16, 59, 0),
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=27,
            ejudge_status=EjudgeStatusesEnum.COMPILING,
        )
        db.session.add(run)
        db.session.flush()
        db.session.refresh(run)

        file = self.file_mock

        text = file.read()
        run.update_source(text)

        submit = Submit(
            id=1,
            user_id=self.users[0].id,
            run_id=run.id,
            ejudge_url='ejudge_url',
        )

        ejudge_submit_mock.side_effect = lambda *args, **kwargs: 1 / 0
        assert_that(
            calling(submit.send),
            is_not(raises(anything())),
        )

        notify_user_mock.assert_called_once_with(
            self.users[0].id,
            'SUBMIT_ERROR',
            {
                'ejudge_error': {
                    'code': None,
                    'message': 'Ошибка отправки задачи'
                }
            }
        )

        ejudge_submit_mock.side_effect = None

    def test_handles_submit_error(self):
        # В случае, если ejudge вернул не 0 код

        run = Run(
            user_id=self.users[0].id,
            problem_id=self.problems[0].id,
            statement_id=self.statements[0].id,
            create_time=datetime.datetime(2018, 3, 30, 17, 10, 11),
            ejudge_contest_id=self.problems[0].ejudge_contest_id,
            ejudge_language_id=27,
            ejudge_status=EjudgeStatusesEnum.COMPILING,
        )
        db.session.add(run)
        db.session.flush()
        db.session.refresh(run)

        file = self.file_mock

        text = file.read()
        run.update_source(text)

        submit = Submit(
            id=1,
            user_id=self.users[0].id,
            run_id=run.id,
            ejudge_url='ejudge_url',
        )

        ejudge_submit_mock.return_value = {
            'code': 123,
            'message': 'some message',
            'other': 'secrets'
        }
        assert_that(
            calling(submit.send),
            is_not(raises(anything())),
        )

        notify_user_mock.assert_called_once_with(
            self.users[0].id,
            'SUBMIT_ERROR',
            {
                'ejudge_error': {
                    'code': 123,
                    'message': 'some message'
                }
            }
        )

        ejudge_submit_mock.side_effect = None
