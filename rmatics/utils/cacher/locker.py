from abc import ABC, abstractmethod
import time
from contextlib import contextmanager

from redlock import Redlock


class ILocker(ABC):
    @abstractmethod
    def _lock(self, key, timeout):
        pass

    @abstractmethod
    def _unlock(self, key):
        pass

    @contextmanager
    def take_possession(self, key, timeout=4000):
        """ Context manager for locking some resource """
        self._lock(key, timeout)
        yield
        self._unlock(key)


class FakeLocker(ILocker):
    def _lock(self, *args, **kwargs):
        pass

    def _unlock(self, *args, **kwargs):
        pass


class RedisLocker(ILocker):
    def __init__(self, redis_con):
        self.dlm = Redlock([redis_con, ], retry_count=1)
        self._locks = {}

    def _lock(self, key, timeout):
        """ Trying to acquire lock
            If not success then sleep (timeout // 10) milliseconds
            and try again
        """
        lock_key = f'lock/{key}'
        sleep_time = timeout / (10 * 1000)
        while True:
            lock = self.dlm.lock(lock_key, timeout)
            if lock:
                break
            time.sleep(sleep_time)

        self._locks[lock_key] = lock

    def _unlock(self, key):
        lock_key = f'lock/{key}'
        lock = self._locks[lock_key]
        self.dlm.unlock(lock)
