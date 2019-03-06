import datetime
from abc import ABC, abstractmethod
from typing import Callable, List

from sqlalchemy import or_, and_

from rmatics import db
from rmatics.model import CacheMeta


class ICacheInvalidator(ABC):

    @abstractmethod
    def init_app(self, remove_cache_func: Callable[[str], None]):
        pass

    @abstractmethod
    def subscribe(self, label: str, period: int, key: str, func_kwargs: dict, **kwargs):
        pass

    @abstractmethod
    def invalidate(self, label: str, all_of: dict = None, any_of: dict = None) -> bool:
        pass


class MonitorCacheInvalidator(ICacheInvalidator):
    def __init__(self, autocommit=True, prefix=None):
        self.remove_cache_func = None
        self.autocommit = autocommit
        self.prefix = prefix or 'monitor'
        self.invalidate_by = ['problem_id', 'user_ids',
                              'time_after', 'time_before']

    def init_app(self, remove_cache_func: Callable[[str], None], period=20):
        self.remove_cache_func = remove_cache_func

    def subscribe(self, label: str, period: int, key: str, func_kwargs: dict, **kwargs):
        when_expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=period)

        invalidate_kwargs = self._filter_invalidate_kwargs(func_kwargs)

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

    def invalidate(self, label: str, all_of: dict = None, any_of: dict = None) -> bool:
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

        invalid_cache_metas = db.session.query(CacheMeta) \
            .filter(CacheMeta.prefix == self.prefix) \
            .filter(CacheMeta.label == label) \
            .filter(or_(CacheMeta.invalidate_args.like(a) for a in any_like_args)) \
            .filter(and_(CacheMeta.invalidate_args.like(a) for a in all_like_args))

        for meta in invalid_cache_metas:
            self.remove_cache_func(meta.key)
            db.session.delete(meta)

        if self.autocommit:
            db.session.commit()

        return True

    def _filter_invalidate_kwargs(self, kwargs: dict) -> dict:
        result_set = {}
        for arg in self.invalidate_by:
            val = kwargs.get(arg)
            if val is not None:
                result_set[arg] = val
        return result_set

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

    @staticmethod
    def _simple_item_to_string(key, item):
        return f'{key}_{item}'

    @classmethod
    def _list_item_to_string(cls, key, value):
        acc = []
        for item in value:
            acc.append(cls._simple_item_to_string(key, item))
        return acc
