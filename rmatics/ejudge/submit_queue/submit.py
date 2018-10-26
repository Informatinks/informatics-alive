import io
import logging
from flask import current_app, g
from werkzeug.datastructures import FileStorage

from rmatics.ejudge.ejudge_proxy import submit
from rmatics.model import db
from rmatics.model.run import Run
from rmatics.model.user import SimpleUser
from rmatics.model.problem import EjudgeProblem
from rmatics.utils.functions import attrs_to_dict
from rmatics.websocket import notify_user
from rmatics.websocket.events import (
    SUBMIT_ERROR,
    SUBMIT_SUCCESS
)


log = logging.getLogger('submit_queue')


def ejudge_error_notification(ejudge_response=None):
    code = None
    message = 'Ошибка отправки задачи'
    try:
        code = ejudge_response['code']
        message = ejudge_response['message']
    except Exception:
        pass
    return {
        'ejudge_error': {
            'code': code,
            'message': message,
        }
    }


class Submit:
    def __init__(self,
                 id,
                 user_id,
                 problem_id,
                 create_time,
                 file,
                 language_id,
                 ejudge_url,
                 statement_id=None,
                 ):
        self.id = id
        self.user_id = user_id
        self.problem_id = problem_id
        self.create_time = create_time
        self.file = file
        self.language_id = language_id
        self.ejudge_url = ejudge_url
        self.statement_id = statement_id
        self.ejudge_user = current_app.config.get('EJUDGE_USER')
        self.ejudge_password = current_app.config.get('EJUDGE_PASSWORD')

    @property
    def user(self):
        if not hasattr(self, '_user'):
            self._user = db.session.query(SimpleUser) \
                .filter_by(id=self.user_id) \
                .first()
        return self._user

    @property
    def problem(self):
        if not hasattr(self, '_problem'):
            self._problem = db.session.query(EjudgeProblem) \
                .filter_by(id=self.problem_id) \
                .first()
        return self._problem

    @property
    def source(self):
        if not hasattr(self, '_source'):
            self._source = self.file.read().decode('utf-8')
            self.file.seek(0)
        return self._source

    def send(self):
        try:
            ejudge_response = submit(
                run_file=self.file,
                contest_id=self.problem.ejudge_contest_id,
                prob_id=self.problem.problem_id,
                lang_id=self.language_id,
                login=self.ejudge_user,
                password=self.ejudge_password,
                filename=self.file.filename,
                url=self.ejudge_url,
                user_id=self.user.id
            )
        except Exception:
            log.exception('Unknown Ejudge submit error')
            notify_user(self.user.id, SUBMIT_ERROR, ejudge_error_notification())
            return

        try:
            if ejudge_response['code'] != 0:
                notify_user(self.user.id, SUBMIT_ERROR, ejudge_error_notification(ejudge_response))
                return

            run_id = ejudge_response['run_id']
        except Exception:
            log.exception('ejudge_proxy.submit returned bad value')
            notify_user(self.user.id, SUBMIT_ERROR, message=ejudge_error_notification())
            return

        run = Run(
            user_id=self.user.id,
            problem=self.problem,
            statement_id=self.statement_id,
            create_time=self.create_time,
            ejudge_run_id=run_id,
            ejudge_contest_id=self.problem.ejudge_contest_id,
            ejudge_language_id=self.language_id,
            ejudge_status=98,  # compiling
        )
        db.session.add(run)
        db.session.commit()

        db.session.refresh(run)
        run.update_source(text=self.source)
        g.user = self.user
        notify_user(
            self.user.id,
            SUBMIT_SUCCESS,
            {
                'run': run.serialize(),
                'submit_id': self.id,
            }
        )

    def encode(self):
        file = self.file.read()
        self.file.seek(0)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'create_time': self.create_time,
            'file': file,
            'filename': self.file.filename,
            'language_id': self.language_id,
            'ejudge_url': self.ejudge_url,
            'statement_id': self.statement_id,
        }

    @staticmethod
    def decode(encoded):
        return Submit(
            id=encoded['id'],
            user_id=encoded['user_id'],
            problem_id=encoded['problem_id'],
            create_time=encoded['create_time'],
            file=FileStorage(
                stream=io.BytesIO(encoded['file']),
                filename=encoded['filename'],
            ),
            language_id=encoded['language_id'],
            ejudge_url=encoded['ejudge_url'],
            statement_id=encoded['statement_id'],
        )

    def serialize(self, attributes=None):
        if attributes is None:
            attributes = (
                'id',
                'user_id',
                'problem_id',
                'source',
                'language_id',
            )
        serialized = attrs_to_dict(self, *attributes)
        if 'user_id' in attributes:
            serialized['user_id'] = self.user.id
        if 'problem_id' in attributes:
            serialized['problem_id'] = self.problem.id
        return serialized
