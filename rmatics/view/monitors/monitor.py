import datetime
from collections import namedtuple
from typing import Iterable

from flask import request
from marshmallow import fields
from webargs.flaskparser import parser
from flask.views import MethodView
from sqlalchemy.orm import joinedload, Load, load_only

from rmatics import db, monitor_cacher
from rmatics.model import CourseModule, StatementProblem, Problem, \
    SimpleUser, Run, UserGroup
from rmatics.utils.response import jsonify
from rmatics.view.monitors.serializers.monitor import ContestMonitorSchema, RunSchema


MonitorData = namedtuple('MonitorData', ('contest_id', 'problem', 'runs'))


@monitor_cacher
def get_runs(problem_id: int = None, user_ids: Iterable = None,
             time_after: int = None, time_before: int = None):
    """"""
    query = db.session.query(Run) \
        .join(SimpleUser, SimpleUser.id == Run.user_id)

    if problem_id is not None:
        query = query.filter(Run.problem_id == problem_id)

    if user_ids is not None:
        query = query.filter(SimpleUser.id.in_(user_ids))

    if time_after is not None:
        time_after = datetime.datetime.fromtimestamp(time_after)
        query = query.filter(Run.create_time > time_after)
    if time_before is not None:
        time_before = datetime.datetime.fromtimestamp(time_before)
        query = query.filter(Run.create_time < time_before)

    load_only_fields = [
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
                .options(joinedload(Run.user)
                         .load_only('id', 'firstname', 'lastname')) \
                .options(Load(Run).load_only(*load_only_fields))

    schema = RunSchema(many=True)
    data = schema.dump(runs.all())
    return data.data


get_args = {
    'group_id': fields.Integer(required=True),
    'contest_id': fields.List(fields.Integer(), required=True),
    'time_before': fields.Integer(missing=None),
    'time_after': fields.Integer(missing=None),
}


class MonitorAPIView(MethodView):
    def get(self):
        args = parser.parse(get_args, request)

        contest_ids = args['contest_id']
        group_id = args['group_id']
        time_before = args['time_before']
        time_after = args['time_after']

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
                runs = get_runs(problem_id=problem.id,
                                user_ids=user_ids,
                                time_before=time_before,
                                time_after=time_after)
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
        """
         SELECT
            mdl_problems.id,
            mdl_statements_problems_correlation.rank,
            mdl_problems.name,
            mdl_statements_problems_correlation.hidden as cur_hidden,
            mdl_ejudge_problem.short_id,
            mdl_problems.pr_id,
            mdl_ejudge_problem.contest_id
        FROM
            mdl_problems, mdl_statements_problems_correlation, mdl_ejudge_problem
        WHERE
            mdl_ejudge_problem.id = mdl_problems.pr_id AND
            mdl_statements_problems_correlation.problem_id = mdl_problems.id AND
            mdl_statements_problems_correlation.statement_id = 20078
        ORDER BY
            mdl_statements_problems_correlation.rank 
        """

        problems = db.session.query(Problem) \
            .join(StatementProblem, StatementProblem.problem_id == Problem.id) \
            .filter(StatementProblem.statement_id == statement.id) \
            .options(joinedload(Problem.ejudge_problem)
                     .load_only('id', 'short_id')) \
            .options(load_only('id', 'name', 'pr_id'))

        return problems.all()
