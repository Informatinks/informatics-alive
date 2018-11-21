from flask import current_app
from cent import Client, CentException

from rmatics.model.run import Run


class CentrifugoClient:
    client: Client = None

    def init_app(self, url, api_key):
        self.client = Client(url, api_key=api_key, timeout=1, verify=False)

    def send_problem_run_updates(self, problem_id: int, run: Run):
        current_app.logger.debug(f'CentrifugoClient: send update for problem {problem_id}')
        channel = f'problem.{problem_id}'
        try:
            self.client.publish(channel, {'run': run.serialize()})
        except AttributeError:
            current_app.logger.exception(f'CentrifugoClient: client is not initialized')
        except CentException:
            current_app.logger.exception(f'CentrifugoClient: can\'t send message to centrifugo')


centrifugo_client = CentrifugoClient()
