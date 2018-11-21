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
        self.create_problems()

    def test_submit_get(self):
        queue = SubmitQueue(key='some.key')

        queue.submit(
            user_id=1,
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
                user_id=1,
                run_id=123,
                ejudge_url='ejudge_url',
            )

            assert_that(int(redis.get('some.key:last.put.id')), equal_to(i + 1))
            assert_that(redis.get('some.key:last.get.id'), equal_to(None))

        for i in range(5):
            queue.get()

            assert_that(int(redis.get('some.key:last.put.id')), equal_to(5))
            assert_that(int(redis.get('some.key:last.get.id')), equal_to(i + 1))

    def test_with_workers(self):
        queue = SubmitQueue()
        from gevent import monkey
        monkey.patch_all()
        worker = SubmitWorker(queue)
        worker.start()

        with mock.patch.object(Submit, 'send', autospec=True) as send_mock:

            queue.submit(123, 1, 'ejudge_url')

            time.sleep(1)
            assert_that(send_mock.call_count, equal_to(1))

            submit_from_queue = send_mock.call_args[0][0]
            assert_that(submit_from_queue.user_id, equal_to(1))


    def test_peek_user_submits(self):
        queue = SubmitQueue(key='some.key')

        queue.submit(
            run_id=123,
            user_id=1,
            ejudge_url='ejudge_url',
        )
        queue.submit(
            run_id=124,
            user_id=1,
            ejudge_url='ejudge_url',
        )
        queue.submit(
            run_id=125,
            user_id=2,
            ejudge_url='ejudge_url',
        )

        submits = queue.peek_user_submits(user_id=1)
        assert_that(len(submits), equal_to(2))
        assert_that(submits[0].user_id, equal_to(1))
        assert_that(submits[1].user_id, equal_to(1))

        submits = queue.peek_user_submits(user_id=2)
        assert_that(len(submits), equal_to(1))
        assert_that(submits[0].user_id, equal_to(2))

    def test_peek_all_submits(self):
        queue = SubmitQueue(key='some.key')

        queue.submit(
            run_id=123,
            user_id=1,
            ejudge_url='ejudge_url',
        )

        queue.submit(
            run_id=123,
            user_id=1,
            ejudge_url='ejudge_url',
        )
        queue.submit(
            run_id=123,
            user_id=2,
            ejudge_url='ejudge_url',
        )

        submits = queue.peek_all_submits()
        assert_that(len(submits), equal_to(3))
