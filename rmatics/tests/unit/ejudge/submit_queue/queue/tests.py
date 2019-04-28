import mock
import time

from hamcrest import (
    assert_that,
    equal_to,
)

from rmatics.ejudge.submit_queue.queue import SubmitQueue
from rmatics.ejudge.submit_queue.submit import Submit
from rmatics.ejudge.submit_queue.worker import SubmitWorker
from rmatics.model.base import redis
from rmatics.testutils import TestCase


class TestEjudge__submit_queue_submit_queue(TestCase):
    def setUp(self):
        super(TestEjudge__submit_queue_submit_queue, self).setUp()

        self.create_users()
        self.create_ejudge_problems()

    def test_submit_get(self):
        queue = SubmitQueue(key='some.key')

        queue.submit(
            run_id=123,
            ejudge_url='ejudge_url',
        )

        assert_that(int(redis.get('some.key:last.put.id')), equal_to(1))
        assert_that(redis.get('some.key:last.get.id'), equal_to(None))

        submit = queue.get()
        assert_that(submit.id, equal_to(1))

        assert_that(submit.ejudge_url, equal_to('ejudge_url'))

        assert_that(int(redis.get('some.key:last.put.id')), equal_to(1))
        assert_that(int(redis.get('some.key:last.get.id')), equal_to(1))

    def test_last_put_get_id(self):
        queue = SubmitQueue(key='some.key')

        for i in range(5):
            queue.submit(
                run_id=123,
                ejudge_url='ejudge_url',
            )

            assert_that(int(redis.get('some.key:last.put.id')), equal_to(i + 1))
            assert_that(redis.get('some.key:last.get.id'), equal_to(None))

        for i in range(5):
            queue.get()

            assert_that(int(redis.get('some.key:last.put.id')), equal_to(5))
            assert_that(int(redis.get('some.key:last.get.id')), equal_to(i + 1))
