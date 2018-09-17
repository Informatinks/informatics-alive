import datetime
from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.ejudge.submit_queue.submit import Submit
from rmatics.testutils import TestCase


class TestEjudge__submit_queue_submit_decode(TestCase):
    def setUp(self):
        super(TestEjudge__submit_queue_submit_decode, self).setUp()

        self.create_users()
        self.create_problems()
        self.create_statements()

    def test_simple(self):
        submit = Submit.decode({
            'id': 'id',
            'user_id': self.users[0].id,
            'problem_id': self.problems[0].id,
            'context': 'context',
            'create_time': datetime.datetime(2018, 3, 30, 17, 10, 11),
            'file': b'file',
            'filename': 'filename',
            'language_id': 'language_id',
            'ejudge_url': 'ejudge_url',
            'statement_id': self.statements[0].id,
        })
        assert_that(submit.id, equal_to('id'))
        assert_that(submit.user_id, equal_to(self.users[0].id))
        assert_that(submit.problem_id, equal_to(self.problems[0].id))
        assert_that(submit.create_time, equal_to(datetime.datetime(2018, 3, 30, 17, 10, 11)))
        assert_that(submit.file.read(), equal_to(b'file'))
        assert_that(submit.file.filename, equal_to('filename'))
        assert_that(submit.language_id, equal_to('language_id'))
        assert_that(submit.ejudge_url, equal_to('ejudge_url'))
        assert_that(submit.statement_id, equal_to(self.statements[0].id))
