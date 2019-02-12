import time

from flask import current_app
from redlock import Redlock

from rmatics.testutils import TestCase
from rmatics.utils.cacher.locker import RedisLocker


RESOURCE_KEY = 'abc'

LOCK_TIME_MSEC = 400


class TestRedisLocker(TestCase):
    def setUp(self):
        super().setUp()

        self.lock = RedisLocker(current_app.config['REDIS_URL'])
        another_lock = Redlock([current_app.config['REDIS_URL'], ], retry_count=1)
        self.another_locker = another_lock

    def test_locked(self):
        with self.lock.take_possession(RESOURCE_KEY):
            lock = self.another_locker.lock(f'lock/{RESOURCE_KEY}', LOCK_TIME_MSEC)
        self.assertFalse(lock, 'Lock acquired by RedisLocker')

        lock = self.another_locker.lock(RESOURCE_KEY, LOCK_TIME_MSEC)
        self.assertNotEqual(False, lock, 'Lock from RedisLocker realised')

        # Actually it is side effect so we should realise another_locker
        self.another_locker.unlock(lock)

    def test_unlock_after(self):
        time_start = time.time()
        self.another_locker.lock(f'lock/{RESOURCE_KEY}', LOCK_TIME_MSEC)

        with self.lock.take_possession(RESOURCE_KEY, LOCK_TIME_MSEC):
            time_stop = time.time()

        spent_time = time_stop - time_start

        self.assertTrue(spent_time >= LOCK_TIME_MSEC / 1000,
                        'We have to sleep until another_lock is not expired')



