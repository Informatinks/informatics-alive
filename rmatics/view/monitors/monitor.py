from collections import namedtuple
from typing import Iterable

from flask import request
from marshmallow import fields
from webargs.flaskparser import parser
from flask.views import MethodView
from sqlalchemy.orm import joinedload, Load

from rmatics import db, monitor_cacher
from rmatics.model import CourseModule, StatementProblem, Problem, \
    SimpleUser, Run, UserGroup, EjudgeProblem
from rmatics.utils.response import jsonify
from rmatics.view.monitors.serializers.monitor import ContestMonitorSchema, RunSchema


MonitorData = namedtuple('MonitorData', ('contest_id', 'problem', 'runs'))


@monitor_cacher
def get_runs(problem_id: int = None, user_ids: Iterable = None):
    query = db.session.query(Run) \
        .join(SimpleUser, SimpleUser.id == Run.user_id)

    if problem_id is not None:
        query = query.filter(Run.problem_id == problem_id)

    if user_ids is not None:
        query = query.filter(SimpleUser.id.in_(user_ids))

    load_only = [
        'id',
        'user_id',
        'create_time',
        'ejudge_run_id',
        'ejudge_contest_id',
        'ejudge_score',
        'ejudge_status',
        'ejudge_test_num'
    ]

    runs = query.order_by(Run.id) \
                .options(joinedload(Run.user)) \
                .options(Load(Run).load_only(*load_only)) \
                .all()
    schema = RunSchema(many=True)
    data = schema.dump(runs)
    return data.data


get_args = {
    'group_id': fields.Integer(required=True),
    'contest_id': fields.List(fields.Integer(), required=True),
}


class MonitorAPIView(MethodView):
    def get(self):
        args = parser.parse(get_args, request)

        contest_ids = args['contest_id']
        group_id = args['group_id']

        users = db.session.query(SimpleUser)\
            .join(UserGroup, UserGroup.user_id == SimpleUser.id)\
            .filter(UserGroup.group_id == group_id)

        user_ids = [user.id for user in users]

        contest_problems = {}
        for contest_id in contest_ids:
            contest_problems[contest_id] = self._get_ejudge_problems(contest_id)

        contest_problems_runs = []
        for contest_id, problems in contest_problems.items():
            for problem in problems:
                runs = get_runs(problem_id=problem.id, user_ids=user_ids)
                monitor_data = MonitorData(contest_id, problem, runs)
                contest_problems_runs.append(monitor_data)

        schema = ContestMonitorSchema(many=True)

        # TODO: Подумать, как лучше вернуть
        response = schema.dump(contest_problems_runs)

        return jsonify(response.data)

    @classmethod
    def _get_ejudge_problems(cls, contest_id) -> list:
        """ Get all problems from is's id """

        cm = CourseModule
        course_module = db.session.query(cm).filter(cm.id == contest_id).one_or_none()
        if course_module is None:
            return []
        statement = course_module.instance

        sp = StatementProblem
        statements_problems = db.session.query(sp) \
            .join(EjudgeProblem, EjudgeProblem.ejudge_prid == Problem.pr_id) \
            .filter(sp.statement_id == statement.id) \
            .options(joinedload(sp.problem)) \
            .options(Load(Problem).load_only('id', 'name')) \
            .options(Load(EjudgeProblem).load_only('id', 'short_id'))

        return list(map(lambda sp: sp.problem, statements_problems))
