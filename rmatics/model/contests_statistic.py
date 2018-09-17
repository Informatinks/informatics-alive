from rmatics.model import db


class ContestsStatistic(db.Model):
    __table_args__ = {'schema':'moodle'}
    __tablename__ = 'contests_statistic'

    contest_id = db.Column(db.Integer, primary_key=True)
    submits_count = db.Column(db.Integer)
