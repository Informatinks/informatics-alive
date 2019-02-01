import datetime
from typing import Iterable, List

from rmatics.model.base import db


MAX_KEY_LEN = 4096


class CacheMeta(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'cache_meta'

    id = db.Column(db.Integer(), primary_key=True)

    prefix = db.Column(db.String(30), nullable=False)
    label = db.Column(db.String(30), nullable=False)
    key = db.Column(db.String(64), nullable=False)

    invalidate_args = db.Column(db.String(MAX_KEY_LEN))

    created = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    when_expire = db.Column(db.DateTime(), nullable=False)

    @classmethod
    def get_invalidate_args(cls, data: Iterable[str]):
        """ [problem_1, problem_2] -> '|problem_1|problem_2|' """
        return f'|{"|".join(data)}|'[:MAX_KEY_LEN + 1]

    @classmethod
    def _get_search_arg(cls, arg: str):
        return f'|{arg}|'

    @classmethod
    def _get_like_args(cls, args: Iterable[str]) -> Iterable[str]:
        return map(lambda a: f'%{a}%', args)

    @classmethod
    def get_search_like_args(cls, args: Iterable[str]) -> List[str]:
        """ [problem_1] -> ['%|problem_1|%'] """
        return list(cls._get_like_args(map(cls._get_search_arg, args)))

