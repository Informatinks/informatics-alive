import datetime
from collections import namedtuple, OrderedDict
from typing import Iterable, Tuple, Optional

from flask import request
from marshmallow import fields
from webargs.flaskparser import parser
from flask.views import MethodView
from sqlalchemy.orm import joinedload, Load

from rmatics import db, monitor_cacher
from rmatics.model import SimpleUser, Run, UserGroup, CourseModule, Statement, MonitorCourseModule
from rmatics.model.monitor import MonitorStatement, Monitor
from rmatics.utils.response import jsonify
from rmatics.view import get_problems_by_statement_id
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
    'group_id': fields.Integer(missing=None),
    'contest_id': fields.List(fields.Integer(), required=True),
    'time_before': fields.Integer(missing=None),
    'time_after': fields.Integer(missing=None),
}


class MonitorAPIView(MethodView):
    def get(self):
        args = parser.parse(get_args, request)

        course_module_ids = args['contest_id']
        group_id = args['group_id']
        time_before = args['time_before']
        time_after = args['time_after']

        contest_ids = []
        for cm_id in course_module_ids:
            monitor_group_id, statement_ids = self._get_contests(cm_id)
            contest_ids += statement_ids
            group_id = group_id or monitor_group_id

        if group_id:
            users = db.session.query(SimpleUser)\
                .join(UserGroup, UserGroup.user_id == SimpleUser.id)\
                .filter(UserGroup.group_id == group_id)
            user_ids = [user.id for user in users]
        else:
            user_ids = None

        contest_problems = OrderedDict()
        for contest_id in contest_ids:
            contest_problems[contest_id] = get_problems_by_statement_id(contest_id)

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

        # We have to commit session because we may created cache_meta
        db.session.commit()

        return jsonify(response.data)

    @classmethod
    def _get_contests(cls, course_module_id: int) -> Tuple[Optional[int], list]:
        """
        Returns
        -------
        if cm is Monitor:
            Monitor.group_id, [statement_id]
        if cm was Statement:
             None, [statement_id]
        """
        cm = CourseModule
        course_module = db.session.query(cm).filter(cm.id == course_module_id).one_or_none()
        if course_module is None:
            return None, []
        course_module_instance = course_module.instance

        if isinstance(course_module_instance, Statement):
            return None, [course_module_instance.id]

        elif isinstance(course_module_instance, MonitorCourseModule):
            statement_ids = db.session.query(MonitorStatement.statement_id) \
                .join(Monitor, Monitor.id == MonitorStatement.monitor_id) \
                .join(MonitorCourseModule, MonitorCourseModule.monitor_id == Monitor.id) \
                .filter(MonitorCourseModule.id == course_module_instance.id) \
                .order_by(MonitorStatement.sort) \
                .all()
            statement_ids = [s[0] for s in statement_ids]
            return course_module_instance.group_id, statement_ids

        return None, []
