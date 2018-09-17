from flask import current_app
from gevent import Greenlet, sleep


class SubmitWorker(Greenlet):
    def __init__(self, queue):
        super(SubmitWorker, self).__init__()
        self.queue = queue
        self._ctx = current_app.app_context()

    def handle_submit(self):
        submit = self.queue.get()
        try:
            submit.send()
        except Exception:
            current_app.logger.exception('Submit worker caught exception and skipped submit without notifying user')

    def _run(self):
        with self._ctx:
            while True:
                self.handle_submit()
