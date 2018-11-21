from sqlalchemy import and_

from rmatics.model.base import db


class Hint(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'sis_hint'

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('moodle.mdl_problems.id'))
    contest_id = db.Column(db.Integer, db.ForeignKey('ejudge.runs.contest_id'))
    lang_id = db.Column(db.Integer)
    test_signature = db.Column(db.Unicode(255))
    comment = db.Column(db.Text)

    def __init__(self, problem_id, contest_id, lang_id, test_signature, comment):
        self.problem_id = problem_id
        self.contest_id = contest_id
        self.lang_id = lang_id
        self.test_signature = test_signature
        self.comment = comment
        
    def get_by(contest_id, problem_id, lang_id, signature):
        try:  # lang_id is ignored, cause we don't have hints for each language
            return db.session.query(Hint) \
                .filter(Hint.contest_id == int(contest_id)) \
                .filter(Hint.problem_id == int(problem_id)) \
                .filter(Hint.test_signature == signature) \
                .first()            
        except:
            return None

    def __json__(self, request):
        return {
            'id' :  self.id,
            'problem_id' : self.problem_id,
            'contest_id': self.contest_id,
            'lang_id' : self.lang_id,
            'test_signature' : self.test_signature,
            'comment': self.comment,
        }
