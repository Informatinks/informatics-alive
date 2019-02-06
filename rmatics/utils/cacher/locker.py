from abc import ABC

from redlock import Redlock


class ILocker(ABC):
    def lock(self, key, time=4000):
        pass

    def unlock(self, key):
        pass


class FakeLocker(ABC):
    def lock(self, *args, **kwargs):
        pass

    def unlock(self, *args, **kwargs):
        pass


class RedisLocker(ILocker):
    def __init__(self, redis_con):
        self.dlm = Redlock([redis_con, ])
        self._locks = {}

    def lock(self, key, time=4000):
        self._locks[key] = self.dlm.lock(key, time)

    def unlock(self, key):
        lock = self._locks[key]
        self.dlm.unlock(lock)

