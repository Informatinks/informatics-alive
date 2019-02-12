import datetime
import functools
import hashlib
import json
import pickle
from typing import Callable, List

import redis
from sqlalchemy import or_, and_

from rmatics.model.base import db
from rmatics.model.cache_meta import CacheMeta
from rmatics.utils.cacher.locker import ILocker

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
        monitor_cacher = Cacher(store, can_invalidate=True,
                                invalidate_args=['problem_ids', 'group_ids'])

        @monitor_cacher
        def get_monitor(problem_ids: list = None, group_ids: list = None) -> Json serializable:
            ...

        problem_ids = [1, 2, 3]
        group_ids = [3, 4, 5]
        # Function executed; Cache updated
        data = get_monitor(problem_ids=problem_ids, group_ids=group_ids)
        # Returns cached data
        data = get_monitor(problem_ids=problem_ids)

        expired_contests = [1]
        # Invalidate cache for all get_monitor with expired_contests in problem_ids
        monitor_cacher.invalidate_any_of(get_monitor,
                                         problem_ids=expired_problems)

        expired_contests = [1]
        group_id = 3
        # Invalidate cache for all get_monitor
        # with expired_contests in problem_ids and group_id in group_ids
        monitor_cacher.invalidate_all_of(get_monitor,
                                         problem_ids=expired_problems, group_ids=3)

        # Function executed; Cache updated
        data = get_monitor(problem_ids=contest_ids, group_ids=group_ids)

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
        Инвалидация работает только для kwargs со списками и одиночными значениями
        Например, contest_ids = [1, 2, 3]; для contest_ids = {id: [3]} не сработает
    Also #4:
    ------
        We can use locker to lock storage;
        Before getting from cache we lock our code and then realise it
        to avoid raise conditions and multiply function executing
        lock is unique for each cache key (from get_cache_key)
    """
    def __init__(self, store,
                 locker: ILocker,
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
        self.locker = locker
        if can_invalidate and not self.invalidate_by:
            raise ValueError('You must specify any invalidate_by args for invalidating')

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Parameter to check if caching is disabled
            # monitors.get_monitor(1, cache=False)
            to_be_cached = kwargs.pop('cache', True)
            if not to_be_cached:
                return func(*args, **kwargs)

            if self.can_invalidate:
                # If we can invalidate we will better use invalidate_by kwargs only
                invalidate_kwargs = self._filter_invalidate_kwargs(kwargs)
                key = get_cache_key(func, self.prefix, (), invalidate_kwargs)
            else:
                key = get_cache_key(func, self.prefix, args, kwargs)

            with self.locker.take_possession(key):
                try:
                    result = self.store.get(key)
                except redis.exceptions.ConnectionError:
                    return func(*args, **kwargs)

                if result:
                    return json.loads(result)

                func_result = func(*args, **kwargs)
                self.store.set(key, json.dumps(func_result))
                self.store.expire(key, self.period)

                self._save_cache_meta(func, key, invalidate_kwargs)

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
            if value is None:
                continue
            if isinstance(value, list):
                acc += cls._list_item_to_string(key, value)
            else:
                acc.append(cls._simple_item_to_string(key, value))
        return acc

    def _save_cache_meta(self, func, key: str, invalidate_kwargs):

        label = func.__name__
        when_expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=self.period)

        invalidate_args_list = self._kwargs_to_string_list(invalidate_kwargs)
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

    def _filter_invalidate_kwargs(self, kwargs: dict) -> dict:
        result_set = {}
        for arg in self.invalidate_by:
            val = kwargs.get(arg)
            if val is not None:
                result_set[arg] = val
        return result_set

    def invalidate_any_of(self, func, **kwargs) -> bool:
        """ Invalidate all caches of func by given keys if it matches any of key
            Returns True if its possible to invalidate some caches
        """
        if not self.can_invalidate:
            return False

        return self._invalidate(func, any_of=kwargs)

    def invalidate_all_of(self, func, **kwargs) -> bool:
        """ Invalidate all caches of func by given keys if it matches all of keys
            Returns True if its possible to invalidate some caches
        """
        if not self.can_invalidate:
            return False

        return self._invalidate(func, all_of=kwargs)

    def _invalidate(self, func, all_of: dict = None, any_of: dict = None) -> bool:
        any_of = any_of or {}
        all_of = all_of or {}
        all_invalidate_kwargs = self._filter_invalidate_kwargs(all_of)
        any_invalidate_kwargs = self._filter_invalidate_kwargs(any_of)

        if not all_invalidate_kwargs and not any_invalidate_kwargs:
            return False

        strings_all_from_kwargs = self._kwargs_to_string_list(all_invalidate_kwargs)
        strings_any_from_kwargs = self._kwargs_to_string_list(any_invalidate_kwargs)

        all_like_args = CacheMeta.get_search_like_args(strings_all_from_kwargs)
        any_like_args = CacheMeta.get_search_like_args(strings_any_from_kwargs)

        label = func.__name__

        invalid_cache_metas = db.session.query(CacheMeta) \
            .filter(CacheMeta.prefix == self.prefix) \
            .filter(CacheMeta.label == label) \
            .filter(or_(CacheMeta.invalidate_args.like(a) for a in any_like_args)) \
            .filter(and_(CacheMeta.invalidate_args.like(a) for a in all_like_args))

        for meta in invalid_cache_metas:
            self.store.delete(meta.key)
            db.session.delete(meta)

        if self.autocommit:
            db.session.commit()

        return True
