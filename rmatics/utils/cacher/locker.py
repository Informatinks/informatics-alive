from abc import ABC, abstractmethod
import time

from redlock import Redlock


class ILocker(ABC):
    @abstractmethod
    def lock(self, key, timeout=4000):
        pass

    @abstractmethod
    def unlock(self, key):
        pass


class FakeLocker(ILocker):
    def lock(self, *args, **kwargs):
        pass

    def unlock(self, *args, **kwargs):
        pass


class RedisLocker(ILocker):
    def __init__(self, redis_con):
        self.dlm = Redlock([redis_con, ], retry_count=1)
        self._locks = {}

    def lock(self, key, timeout=4000):
        """ Trying to acquire lock
            If not success then sleep (timeout // 10) milliseconds
            and try again
        """
        sleep_time = timeout / (10 * 1000)
        while True:
            lock = self.dlm.lock(key, timeout)
            if not lock:
                time.sleep(sleep_time)
                continue
            break

        self._locks[key] = lock

    def unlock(self, key):
        lock = self._locks[key]
        self.dlm.unlock(lock)

