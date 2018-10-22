import io
from flask import g
from hamcrest import (
    assert_that,
    contains_inanyorder,
    equal_to,
    has_entries,
)

from rmatics.ejudge.submit_queue import queue_submit
from rmatics.testutils import TestCase


class TestAPI__submit_get(TestCase):
    def setUp(self):
        super(TestAPI__submit_get, self).setUp()

        self.create_problems()
        self.create_users()

    def send_request(self, user_id=None):
        if user_id:
            self.set_session({'user_id': user_id})
        response = self.client.get('/submit')
        return response

    def test_simple(self):
        self.set_session({'user_id': self.users[0].id})
        response = self.client.post(
            f'/problem/{self.problems[0].id}/submit_v2',
            data={
                'lang_id': 27,
                'file': (io.BytesIO(b'some code'), 'some_file_name')
            }
        )
        assert_that(response.status_code, equal_to(200))
        response = self.client.post(
            f'/problem/{self.problems[1].id}/submit_v2',
            data={
                'lang_id': 24,
                'file': (io.BytesIO(b'perl submit'), 'some_file_name')
            }
        )
        assert_that(response.status_code, equal_to(200))


        response = self.send_request(user_id=self.users[0].id)
        assert_that(response.status_code, equal_to(200))
        assert_that(response.json, has_entries({'last_get_id': 0, 'submits': has_entries({})}))
        assert_that(
            response.json['submits'],
            has_entries({
                '1': {
                    'id': 1,
                    'user_id': self.users[0].id,
                    'problem_id': self.problems[0].id,
                    'source': 'some code',
                    'language_id': 27,
                },
                '2': {
                    'id': 2,
                    'user_id': self.users[0].id,
                    'problem_id': self.problems[1].id,
                    'source': 'perl submit',
                    'language_id': 24,
                }
            })
        )

    def test_empty(self):
        response = self.send_request(user_id=self.users[0].id)
        assert_that(response.status_code, equal_to(200))
        assert_that(response.json, equal_to({'last_get_id': 0, 'submits': {}}))

    def test_unauthorized(self):
        response = self.send_request()
        assert_that(response.status_code, equal_to(401))
        assert_that(
            response.json,
            has_entries({
                'code': 401,
            })
        )
