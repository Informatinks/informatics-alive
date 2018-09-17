import datetime 

from rmatics.model import db
from rmatics.utils.moodle import get_contest_str_id

class EjudgeContest(db.Model):
    __table_args__ = {'schema':'moodle'}
    __tablename__ = 'mdl_ejudge_contest'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(255))
    ejudge_id = db.Column(db.Unicode(10))
    ejudge_int_id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=False)
    load_time = db.Column(db.DateTime)
    cloned = db.Column(db.Boolean, nullable=False)
    
    def __init__(self, name='', ejudge_int_id=0):
        self.name = name
        self.ejudge_id = get_contest_str_id(ejudge_int_id)
        self.ejudge_int_id = ejudge_int_id
        self.load_time = datetime.datetime.now()
        self.cloned = False