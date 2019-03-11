import datetime
import functools
import hashlib
import json
import pickle
from typing import Callable, List, Optional

import redis

from rmatics.utils.cacher.cache_invalidators import ICacheInvalidator
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
                 allowed_kwargs: list,
                 cache_invalidator: Optional[ICacheInvalidator] = None,
                 prefix='cache',
                 period=30*60,
                 autocommit=True):
        """Construct cache decorator based on the given redis connector."""

        self.store = store
        self.prefix = prefix
        self.period = period
        self.cache_invalidator = cache_invalidator
        self.autocommit = autocommit
        self.locker = locker
        self.allowed_kwargs = allowed_kwargs

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Parameter to check if caching is disabled
            # monitors.get_monitor(1, cache=False)
            to_be_cached = kwargs.pop('cache', True)
            if not to_be_cached:
                return func(*args, **kwargs)

            allowed_kwargs = self._filter_invalidate_kwargs(kwargs)

            key = get_cache_key(func, self.prefix, (), allowed_kwargs)

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

            if self.cache_invalidator is not None:
                self.cache_invalidator.subscribe(func.__name__,
                                                 self.period,
                                                 key,
                                                 allowed_kwargs)
            return func_result
        return wrapped

    def _filter_invalidate_kwargs(self, kwargs: dict) -> dict:
        result_set = {}
        for arg in self.allowed_kwargs:
            val = kwargs.get(arg)
            if val is not None:
                result_set[arg] = val
        return result_set

    def invalidate_any_of(self, func, **kwargs) -> bool:
        """ Invalidate all caches of func by given keys if it matches any of key
            Returns True if its possible to invalidate some caches
        """
        if self.cache_invalidator is None:
            return False

        return self._invalidate(func, any_of=kwargs)

    def invalidate_all_of(self, func, **kwargs) -> bool:
        """ Invalidate all caches of func by given keys if it matches all of keys
            Returns True if its possible to invalidate some caches
        """
        if self.cache_invalidator is None:
            return False

        return self._invalidate(func, all_of=kwargs)

    def _invalidate(self, func, all_of: dict = None, any_of: dict = None) -> bool:
        label = func.__name__
        return self.cache_invalidator.invalidate(label, all_of=all_of, any_of=any_of)
