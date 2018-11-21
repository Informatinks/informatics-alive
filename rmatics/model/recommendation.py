from rmatics.model.base import db


class Recommendation(db.Model):
    __table_args__ = {'schema': 'moodle'}
    __tablename__ = 'sis_most_popular_next_problems_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer)
    contest_id = db.Column(db.Integer)

    recommended_problem_id = db.Column(db.Integer)
    recommended_contest_id = db.Column(db.Integer)

    def __init__(self, contest_id, problem_id, recommended_contest_id, recommended_problem_id):
        self.contest_id = contest_id
        self.problem_id = problem_id
        self.recommended_contest_id = recommended_contest_id
        self.recommended_problem_id = recommended_problem_id

    def get_by(self, contest_id, problem_id):
        try:
            return db.session.query(Recommendation).filter_by(contest_id=int(contest_id), problem_id=int(problem_id))
        except:
            return None

    def __json__(self, request):
        return {
            'id' :  self.id,
            'problem_id' : self.problem_id,
            'contest_id': self.contest_id,
            'recommended_contest_id' : self.lang_id,
            'recommended_problem_id' : self.test_signature,
        }

