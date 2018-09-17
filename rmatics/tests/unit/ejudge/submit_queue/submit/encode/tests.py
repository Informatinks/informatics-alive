import io
import mock
import datetime
from hamcrest import (
    assert_that,
    equal_to,
)
from werkzeug.datastructures import FileStorage

from rmatics.ejudge.submit_queue.submit import Submit
from rmatics.testutils import TestCase


class TestEjudge__submit_queue_submit_encode(TestCase):
    def test_simple(self):
        submit = Submit(
            id=123,
            user_id=11,
            problem_id=22,
            create_time=datetime.datetime(2018, 3, 30, 17, 10, 11),
            file=FileStorage(
                stream=io.BytesIO(b'file'),
                filename='filename'
            ),
            language_id='language_id',
            ejudge_url='ejudge_url',
        )
        assert_that(
            submit.encode(),
            equal_to({
                'id': 123,
                'user_id': 11,
                'problem_id': 22,
                'create_time': datetime.datetime(2018, 3, 30, 17, 10, 11),
                'file': b'file',
                'filename': 'filename',
                'language_id': 'language_id',
                'ejudge_url': 'ejudge_url',
                'statement_id': None,
            })
        )
