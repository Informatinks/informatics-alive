from flask import current_app
from gevent import Greenlet, sleep
from rmatics.model.base import db


class SubmitWorker(Greenlet):
    def __init__(self, queue):
        super(SubmitWorker, self).__init__()
        self.queue = queue
        self._ctx = current_app.app_context()
        self.ejudge_url = current_app.config['EJUDGE_NEW_CLIENT_URL']

    def handle_submit(self):
        submit = self.queue.get()
        try:
            submit.send(ejudge_url=self.ejudge_url)
        except Exception:
            current_app.logger.exception('Submit worker caught exception and skipped submit without notifying user')

        finally:
            # handle_submit вызывается внутри контекста;
            # rollback помогает избегать ошибок с незакрытыми транзакциями
            db.session.rollback()

    def _run(self):
        with self._ctx:
            while True:
                self.handle_submit()
