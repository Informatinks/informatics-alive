import functools
from typing import Optional

from flask import current_app
from sqlalchemy.orm import joinedload
from sqlalchemy import exc as sa_exc

from rmatics import centrifugo_client
from rmatics.ejudge.ejudge_proxy import submit
from rmatics.model.base import db
from rmatics.model.run import Run
from rmatics.utils.functions import attrs_to_dict
from rmatics.utils.run import EjudgeStatuses


ON_SQL_CONNECTION_EXCEPTION_RETRY_COUNT = 4


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


def retry_on_exception(exception_class: Exception, times=3):
    times += 1

    def wrapper(func):
        @functools.wraps(func)
        def retryer(*args, **kwargs):
            last_exc = ValueError('Parameter times should be positive')
            for counter in range(times):
                try:
                    return func(*args, **kwargs)
                except exception_class as e:
                    last_exc = e
            raise last_exc
        return retryer

    return wrapper


class Submit:
    def __init__(self, id, user_id, run_id: int, ejudge_url: str):
        self.id = id
        self.user_id = user_id
        self.run_id = run_id
        self.ejudge_url = ejudge_url
        self.ejudge_user = current_app.config.get('EJUDGE_USER')
        self.ejudge_password = current_app.config.get('EJUDGE_PASSWORD')

    @retry_on_exception(sa_exc.OperationalError, times=4)
    def _get_run(self) -> Optional[Run]:
        run: Run = db.session.query(Run) \
            .options(joinedload(Run.problem)) \
            .get(self.run_id)

        return run

    @retry_on_exception(sa_exc.OperationalError, times=4)
    def _add_info_from_ejudge(self, run, ejudge_run_id,
                              ejudge_url, status: EjudgeStatuses):
        run.ejudge_status = status.value
        run.ejudge_run_id = ejudge_run_id
        run.ejudge_url = ejudge_url

        db.session.add(run)
        db.session.commit()

    @retry_on_exception(sa_exc.OperationalError, times=4)
    def _remove_run(self, run: Run):
        run.remove_source()
        db.session.delete(run)

    def send(self, ejudge_url=None):
        current_app.logger.info(f'Trying to send run #{self.run_id} to ejudge')

        ejudge_url = ejudge_url or self.ejudge_url

        run = self._get_run()

        if run is None:
            current_app.logger.error(f'Run #{self.run_id} is not found')
            return

        problem = run.problem
        db.session.expunge(problem)

        ejudge_language_id = run.ejudge_language_id
        user_id = run.user_id

        file = run.source

        centrifugo_client.send_problem_run_updates(run.problem_id, run)

        try:
            ejudge_response = submit(
                run_file=file,
                contest_id=problem.ejudge_contest_id,
                prob_id=problem.problem_id,
                lang_id=ejudge_language_id,
                login=self.ejudge_user,
                password=self.ejudge_password,
                filename='common_filename',
                url=ejudge_url,
                user_id=user_id
            )
        except Exception:
            current_app.logger.exception('Unknown Ejudge submit error')
            return

        try:
            code = ejudge_response['code']
            if code != 0:
                raise ValueError(f'Ejudge returned status code {code}')
            ejudge_run_id = ejudge_response['run_id']
        except (TypeError, KeyError, ValueError):
            self._remove_run(run)
            current_app.logger.exception(f'Ejudge returned bad response: returned bad value: {ejudge_response}')
            return

        self._add_info_from_ejudge(run, ejudge_run_id,
                                   ejudge_url, EjudgeStatuses.COMPILING)

        current_app.logger.info(f'Run #{self.run_id} successfully updated')

    def encode(self):
        return {
            'id': self.id,
            'run_id': self.run_id,
            'ejudge_url': self.ejudge_url,
            'user_id': self.user_id,
        }

    @staticmethod
    def decode(encoded):
        return Submit(
            id=encoded['id'],
            run_id=encoded['run_id'],
            ejudge_url=encoded['ejudge_url'],
            user_id=encoded['user_id'],
        )

    def serialize(self, attributes=None):
        if attributes is None:
            attributes = (
                'id',
            )
        serialized = attrs_to_dict(self, *attributes)
        return serialized
