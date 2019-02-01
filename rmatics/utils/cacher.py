import datetime
import functools
import hashlib
import json
import pickle
from typing import Callable, List

import redis
from sqlalchemy import or_

from rmatics.model.base import db
from rmatics.model.cache_meta import CacheMeta

PICKLE_ASCII_PROTO = 0


def _dump_to_ascii_str(obj) -> str:
    """Dump object to ascii-encoded string."""
    return pickle.dumps(obj, PICKLE_ASCII_PROTO).decode()


def get_cache_key(func: Callable, prefix: str,
                  args: tuple, kwargs: dict) -> str:
    """Get unique key to be used as cache key in redis or smth."""
    dumped_args = _dump_to_ascii_str(args)
    dumped_kwargs = _dump_to_ascii_str(kwargs)
    key = f'{dumped_args}_{dumped_kwargs}'
    hashed_key = hashlib.md5(key.encode('ascii'))
    return f'{prefix}/{func.__name__}_{hashed_key.hexdigest()}'


class Cacher:
    """ Class for caching functions. Saves function response to store

    Usage:
    ------
        store = Redis()
        monitor_cacher = Cacher(store, can_invalidate=True, invalidate_args=['contests_id'])

        @monitor_cacher
        def get_monitor(problem_ids: list = None):
            ...

        problem_ids = [1, 2, 3]
        # Function executed; Cache updated
        data = get_monitor(problem_ids=problem_ids)
        # Returns cached data
        data = get_monitor(problem_ids=problem_ids)

        expired_contests = [1]
        # Invalidate cache for all get_monitor with expired_contests in problem_ids
        monitor_cacher.invalidate(get_monitor,
                                  problem_ids=expired_contests)
        # Function executed; Cache updated
        data = get_monitor(problem_ids=contest_ids)

    Also #1:
    ------
        For invalidating cache we use DB model CacheMeta
        We use full_text_search by its field
        So its better to remove old CacheMeta
        For example by CRON u now
    Also #2:
    ------
        For invalidation we use only kwargs of cached function call
    Also #3:
    ------
        Инвалидация работает только для kwargs со списками и
        Например, contest_ids = [1, 2, 3]; для contest_ids = {id: [3]} не сработает
    """
    def __init__(self, store,
                 prefix='cache',
                 period=30*60,
                 can_invalidate=True,
                 invalidate_by=None,
                 autocommit=True):
        """Construct cache decorator based on the given redis connector."""

        self.store = store
        self.prefix = prefix
        self.period = period
        self.can_invalidate = can_invalidate
        self.invalidate_by = invalidate_by
        self.autocommit = autocommit

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            key = get_cache_key(func, self.prefix, args, kwargs)

            # Parameter to check if caching is disabled
            # monitors.get_monitor(1, cache=False)
            to_be_cached = kwargs.pop('cache', True)
            if not to_be_cached:
                return func(*args, **kwargs)

            try:
                result = self.store.get(key)
            except redis.exceptions.ConnectionError:
                return func(*args, **kwargs)

            if result:
                return json.loads(result)

            func_result = func(*args, **kwargs)

            self.store.set(key, json.dumps(func_result))
            self.store.expire(key, self.period)

            self._save_cache_meta(func, key, kwargs)

            return func_result
        return wrapped

    @staticmethod
    def _simple_item_to_string(key, item):
        return f'{key}_{item}'

    @classmethod
    def _list_item_to_string(cls, key, value):
        acc = []
        for item in value:
            acc.append(cls._simple_item_to_string(key, item))
        return acc

    @classmethod
    def _kwargs_to_string_list(cls, kwargs: dict) -> List[str]:
        """ {contest: [1, 2], group: 2} -> ['contest_1', 'contest_2', 'group_2']"""
        acc = []
        for key, value in kwargs.items():
            if isinstance(value, list):
                acc += cls._list_item_to_string(key, value)
            else:
                acc.append(cls._simple_item_to_string(key, value))
        return acc

    def _save_cache_meta(self, func, key: str, kwargs):

        label = func.__name__
        when_expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.period)

        invalidate_args_list = self._kwargs_to_string_list(kwargs)
        invalidate_args = CacheMeta.get_invalidate_args(invalidate_args_list)

        cache_meta = CacheMeta(prefix=self.prefix,
                               label=label,
                               key=key,
                               invalidate_args=invalidate_args,
                               when_expire=when_expire)
        db.session.add(cache_meta)
        if self.autocommit:
            db.session.commit()
        return cache_meta

    def invalidate(self, func, **kwargs):
        """ Invalidate all caches of func by given keys """

        strings_from_kwargs = self._kwargs_to_string_list(kwargs)
        like_args = CacheMeta.get_search_like_args(strings_from_kwargs)

        label = func.__name__

        invalid_cache_metas = db.session.query(CacheMeta)\
            .filter(CacheMeta.prefix == self.prefix)\
            .filter(CacheMeta.label == label) \
            .filter(or_(CacheMeta.invalidate_args.like(a) for a in like_args))

        for meta in invalid_cache_metas:
            self.store.delete(meta.key)
            db.session.delete(meta)

        if self.autocommit:
            db.session.commit()
