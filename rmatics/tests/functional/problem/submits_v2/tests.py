import io
from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.ejudge.submit_queue import peek_all_submits
from rmatics.testutils import TestCase


class TestAPI__problem_submits_v2(TestCase):
    def setUp(self):
        super(TestAPI__problem_submits_v2, self).setUp()

        self.create_problems()
        self.create_users()

    def send_request(self, user_id=None, problem_id=None):
        if user_id:
            self.set_session({'user_id': user_id})
        response = self.client.post(
            f'/problem/{problem_id}/submit_v2',
            data={
                'lang_id': 27,
                'file': (io.BytesIO('print("Русский текст")'.encode('utf-8')), 'source.py')
            }
        )
        return response

    def test_simple(self):
        response = self.send_request(
            user_id=self.users[0].id,
            problem_id=self.problems[0].id,
        )

        assert_that(
            response.json,
            equal_to({
                'last_get_id': 0,
                'submit': {
                    'id': 1,
                }
            })
        )
        assert_that(
            len(peek_all_submits()),
            equal_to(1)
        )
