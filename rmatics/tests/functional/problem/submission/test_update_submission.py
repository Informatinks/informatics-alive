from flask import url_for
from mock import patch, MagicMock
from werkzeug.exceptions import NotFound

from rmatics import db
from rmatics.model import Run
from rmatics.testutils import TestCase


class TestAPIUpdateRun(TestCase):
    def setUp(self):
        super().setUp()

        self.create_ejudge_problems()
        self.create_problems()
        self.create_users()

        self.run = Run(user_id=self.users[0].id, problem_id=self.problems[1].id,
                       ejudge_status=1, ejudge_language_id=1)
        db.session.add(self.run)
        db.session.commit()


    def send_request(self, run_id, data: dict):
        url = url_for('problem.run', run_id=run_id)
        resp = self.client.put(url, json=data)
        return resp

    def test_put_not_found_run(self):
        run_id = 777555
        resp = self.send_request(run_id, {})
        self.assert400(resp)

    def test_update_run(self):
        run_id = self.run.id
        with patch('rmatics.utils.cacher.helpers.monitor_cacher') as mc:
            mc.invalidate_all_of = MagicMock()
            self.monitor_invalidate_cache_mock = mc.invalidate_all_of
            resp = self.send_request(run_id, {'ejudge_status': '1488'})
        self.assert200(resp)

        run = db.session.query(Run).get(run_id)
        self.assertEqual(run.ejudge_status, 1488)
        self.monitor_invalidate_cache_mock.assert_called_once()
