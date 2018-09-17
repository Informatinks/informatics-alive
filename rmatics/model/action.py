from sqlalchemy import Column
from sqlalchemy.types import (
    Integer,
    String,
)

from rmatics.model import db


class Action(db.Model):
    __table_args__ = {'schema': 'pynformatics'}
    __tablename__ = 'action'

    id = db.Column(Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(255))

    @staticmethod
    def get_id(description):
        '''
        Возвращает action_id по описанию действия.
        В случае, если такого действия нет, создает его.
        '''
        description = description.upper()
        instance = db.session.query(Action).filter_by(description=description).first()
        if not instance:
            instance = Action(description=description)
            db.session.add(instance)
            db.session.flush([instance])
        return instance.id
