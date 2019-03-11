import json

from mock import MagicMock

from rmatics.testutils import TestCase
from rmatics.utils.cacher import Cacher
from rmatics.utils.cacher.locker import FakeLocker

PREFIX = 'my_cache'
FUNC_NAME = 'my_func_name'
FUNC_RETURN_VALUE = {'data': 'hi!'}


class TestCacher(TestCase):

    def setUp(self):
        super().setUp()

        redis = MagicMock()
        self.redis_get_mock = MagicMock()
        self.redis_set_mock = MagicMock()

        redis.set = self.redis_set_mock
        redis.get = self.redis_get_mock

        locker = FakeLocker()

        self.locker_lock = MagicMock()
        locker._lock = self.locker_lock

        self.locker_unlock = MagicMock()
        locker._unlock = self.locker_unlock

        invalidate_by = ['a', 'problem_id', 'group_id']

        invalidator = MagicMock()
        self.invalidator_subscribe_mock = invalidator.subscribe
        self.invalidator_invalidate_mock = invalidator.invalidate

        self.cacher = Cacher(redis, locker, invalidate_by, prefix='key_prefix', cache_invalidator=invalidator)

        self.to_be_cached = MagicMock(return_value=FUNC_RETURN_VALUE)
        self.to_be_cached.__name__ = FUNC_NAME

        self.cached_function = self.cacher(self.to_be_cached)

    def test_put_to_cache(self):

        self.redis_get_mock.return_value = ''

        res = self.cached_function(a=3)

        self.assertEqual(res, FUNC_RETURN_VALUE)
        self.redis_get_mock.assert_called_once()
        self.redis_set_mock.assert_called_once()

        self.invalidator_subscribe_mock.assert_called_once()

        self.locker_lock.assert_called_once()
        self.locker_unlock.assert_called_once()

    def test_get_from_cache(self):
        another_func_return = {'result': 'imamresult'}
        self.redis_get_mock.return_value = json.dumps(another_func_return)

        res = self.cached_function(a=3)

        self.to_be_cached.assert_not_called()
        self.locker_lock.assert_called_once()
        self.locker_unlock.assert_called_once()

        self.invalidator_subscribe_mock.assert_not_called()
        self.assertEqual(res, another_func_return)
