import json

from mock import MagicMock

from rmatics import db
from rmatics.model.cache_meta import CacheMeta
from rmatics.testutils import TestCase
from rmatics.utils.cacher import Cacher

PREFIX = 'my_cache'
FUNC_NAME = 'my_func_name'
FUNC_RETURN_VALUE = {'data': 'hi!'}


class TestCacher(TestCase):

    def setUp(self):
        super().setUp()

        redis = MagicMock()
        self.redis_get_mock = MagicMock()
        self.redis_set_mock = MagicMock()
        self.redis_delete_mock = MagicMock()

        redis.set = self.redis_set_mock
        redis.get = self.redis_get_mock
        redis.delete = self.redis_delete_mock

        self.cacher = Cacher(redis, prefix=PREFIX)

        self.to_be_cached = MagicMock(return_value=FUNC_RETURN_VALUE)
        self.to_be_cached.__name__ = FUNC_NAME

        self.cached_function = self.cacher(self.to_be_cached)

    def test_put_to_cache(self):

        self.redis_get_mock.return_value = ''

        res = self.cached_function(a=3)

        self.assertEqual(res, FUNC_RETURN_VALUE)
        self.redis_get_mock.assert_called_once()
        self.redis_set_mock.assert_called_once()

        metas = db.session.query(CacheMeta)\
            .filter(CacheMeta.prefix == PREFIX,
                    CacheMeta.label == FUNC_NAME)\
            .count()

        self.assertEqual(metas, 1)

    def test_get_from_cache(self):
        another_func_return = {'result': 'imamresult'}
        self.redis_get_mock.return_value = json.dumps(another_func_return)

        res = self.cached_function(a=3)

        self.to_be_cached.assert_not_called()

        self.assertEqual(res, another_func_return)

    def test_invalidate_cache_not_deleted(self):
        self.redis_get_mock.return_value = ''
        arg_set1 = {'problem_id': [1]}
        arg_set2 = {'problem_id': [2]}
        arg_set3 = {'problem_id': [1, 2, 3]}

        self.cached_function(**arg_set1)
        self.cached_function(**arg_set2)
        self.cached_function(**arg_set3)

        self.cacher.invalidate(self.cached_function, problem_id=0)
        self.redis_delete_mock.assert_not_called()

        metas = db.session.query(CacheMeta) \
            .filter(CacheMeta.prefix == PREFIX,
                    CacheMeta.label == FUNC_NAME) \
            .count()
        self.assertEqual(metas, 3)

    def test_invalidate_cache(self):
        self.redis_get_mock.return_value = ''
        arg_set1 = {'problem_id': [1]}
        arg_set2 = {'problem_id': [2]}
        arg_set3 = {'problem_id': [1, 2, 3]}

        self.cached_function(**arg_set1)
        self.cached_function(**arg_set2)
        self.cached_function(**arg_set3)

        self.cacher.invalidate(self.cached_function, problem_id=1)
        self.assertEqual(self.redis_delete_mock.call_count, 2)

        metas = db.session.query(CacheMeta) \
            .filter(CacheMeta.prefix == PREFIX,
                    CacheMeta.label == FUNC_NAME) \
            .count()
        self.assertEqual(metas, 1)
