from mock import MagicMock

from rmatics import db
from rmatics.model import MonitorCacheMeta
from rmatics.testutils import TestCase
from rmatics.utils.cacher.cache_invalidators import MonitorCacheInvalidator

PREFIX = 'my_cache'
FUNC_NAME = 'my_func_name'
FUNC_KEY = 'my_func_key'


class TestMonitorCacheInvalidator(TestCase):
    def setUp(self):
        super().setUp()

        redis = MagicMock()
        self.redis_delete_mock = MagicMock()
        redis.delete = self.redis_delete_mock

        invalidate_by = ['any_other', 'problem_id', 'any_arg']

        self.invalidator = MonitorCacheInvalidator(autocommit=True)
        self.invalidator.invalidate_by = invalidate_by
        self.invalidator.prefix = PREFIX
        self.invalidator.init_app(remove_cache_func=redis.delete)

    def test_create_cache_meta(self):
        func_kwargs = {
            'problem_id': 1,
            'any_arg': 2,
            'any_other': 'three',
            'not_allowed_invalidate_arg': 'any',
        }
        self.invalidator.subscribe(FUNC_NAME, 10, FUNC_KEY, func_kwargs)

        metas_cnt = db.session.query(MonitorCacheMeta) \
                              .filter(MonitorCacheMeta.prefix == PREFIX,
                                      MonitorCacheMeta.label == FUNC_NAME,
                                      MonitorCacheMeta.problem_id == 1) \
                              .count()

        self.assertEqual(metas_cnt, 1)

        meta = db.session.query(MonitorCacheMeta) \
                         .filter(MonitorCacheMeta.prefix == PREFIX,
                                 MonitorCacheMeta.label == FUNC_NAME) \
                         .first()

        self.assertNotIn('not_allowed_invalidate_arg', meta.invalidate_args)

    def test_cache_invalidated(self):
        func_kwargs = {
            'problem_id': 1,
            'any_arg': 2,
            'any_other': 'three',
        }
        self.invalidator.subscribe(FUNC_NAME, 10, FUNC_KEY, func_kwargs)

        func_kwargs.pop('any_other')
        all_of = func_kwargs

        self.invalidator.invalidate(FUNC_NAME, all_of=all_of)

        metas_cnt = db.session.query(MonitorCacheMeta) \
            .filter(MonitorCacheMeta.prefix == PREFIX,
                    MonitorCacheMeta.label == FUNC_NAME) \
            .count()

        self.assertEqual(metas_cnt, 0)
        self.redis_delete_mock.assert_called_once()

    def test_cache_not_invalidated(self):
        func_kwargs = {
            'problem_id': 1,
            'any_arg': 2,
            'any_other': 'three',
        }
        self.invalidator.subscribe(FUNC_NAME, 10, FUNC_KEY, func_kwargs)

        func_kwargs['any_arg'] = 1
        all_of = func_kwargs

        self.invalidator.invalidate(FUNC_NAME, all_of=all_of)

        metas_cnt = db.session.query(MonitorCacheMeta) \
            .filter(MonitorCacheMeta.prefix == PREFIX,
                    MonitorCacheMeta.label == FUNC_NAME) \
            .count()

        self.assertEqual(metas_cnt, 1, 'Key any_arg is different')

        func_kwargs = {
            'problem_id': 4,
            'any_arg': 2,
            'any_other': 'three',
        }
        all_of = func_kwargs
        self.invalidator.invalidate(FUNC_NAME, all_of=all_of)

        metas_cnt = db.session.query(MonitorCacheMeta) \
            .filter(MonitorCacheMeta.prefix == PREFIX,
                    MonitorCacheMeta.label == FUNC_NAME) \
            .count()

        self.assertEqual(metas_cnt, 1, 'Key Problem is different')

        self.redis_delete_mock.assert_not_called()

    def test_cache_invalidated_with_missing_group(self):
        func_kwargs = {
            'problem_id': 1,
            'any_arg': None,
            'any_other': None,
        }
        self.invalidator.subscribe(FUNC_NAME, 10, FUNC_KEY, func_kwargs)

        meta = db.session.query(MonitorCacheMeta).order_by(MonitorCacheMeta.id.desc()).first()
        self.assertEqual(meta.invalidate_args, '')

        func_kwargs = {
            'problem_id': 1,
            'any_arg': 'something',
            'any_other': 'something else',
        }
        self.invalidator.invalidate(FUNC_NAME, all_of=func_kwargs)
        self.redis_delete_mock.assert_called_once()
