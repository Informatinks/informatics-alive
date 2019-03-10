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
    def __init__(self, id, user_id, run_id: int, ejudge_url: str):
        self.id = id
        self.user_id = user_id
        self.run_id = run_id
        self.ejudge_url = ejudge_url
        self.ejudge_user = current_app.config.get('EJUDGE_USER')
        self.ejudge_password = current_app.config.get('EJUDGE_PASSWORD')

    def _get_and_prepare_run(self) -> Optional[Run]:
        run: Run = db.session.query(Run) \
            .options(joinedload(Run.problem)) \
            .get(self.run_id)

        return run

    def _assign_new_status(self, run: Run):
        run.ejudge_status = EjudgeStatuses.COMPILING.value
        db.session.add(run)
        db.session.commit()

    def _add_info_from_ejudge(self, run, ejudge_run_id, ejudge_url):
        run.ejudge_run_id = ejudge_run_id
        run.ejudge_url = ejudge_url

        db.session.add(run)
        db.session.commit()

    def send(self, ejudge_url=None):
        current_app.logger.info(f'Trying to send run #{self.run_id} to ejudge')

        ejudge_url = ejudge_url or self.ejudge_url

        last_exc = sa_exc.OperationalError
        for counter in range(4):
            try:
                run = self._get_and_prepare_run()
                break
            except sa_exc.OperationalError as e:
                last_exc = e
                current_app.logger.exception(f'Exception while fetching run; try again {counter + 1} time')
        else:
            raise last_exc

        if run is None:
            current_app.logger.error(f'Run #{self.run_id} is not found')
            return

        problem = run.problem
        db.session.expunge(problem)

        ejudge_language_id = run.ejudge_language_id
        user_id = run.user_id

        file = run.source

        # `Run` now not inside the queue so we should change status
        last_exc = sa_exc.OperationalError
        for counter in range(4):
            try:
                self._assign_new_status(run)
                break
            except sa_exc.OperationalError as e:
                last_exc = e
                current_app.logger.exception(f'Exception while fetching run; try again {counter + 1} time')
        else:
            raise last_exc

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
            if ejudge_response['code'] != 0:
                raise TypeError(f'Ejudge returned bad response: {ejudge_response["code"]}')

            ejudge_run_id = ejudge_response['run_id']
        except (TypeError, KeyError, ):
            current_app.logger.exception('ejudge_proxy.submit returned bad value')
            return

        last_exc = sa_exc.OperationalError
        for counter in range(4):
            try:
                self._add_info_from_ejudge(run, ejudge_run_id, ejudge_url)
                break
            except sa_exc.OperationalError as e:
                last_exc = e
                current_app.logger.exception(f'Exception while fetching run; try again {counter + 1} time')
        else:
            raise last_exc

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
