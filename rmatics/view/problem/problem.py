import datetime

from flask import (
    current_app,
    g,
    jsonify,
    request,
)
from werkzeug.exceptions import BadRequest, NotFound
from flask.views import MethodView
from rmatics.ejudge.submit_queue import (
    get_last_get_id,
    queue_submit,
)
from webargs.flaskparser import parser
from marshmallow import fields
from rmatics.model import db
from rmatics.model.group import UserGroup
from rmatics.model.problem import Problem, EjudgeProblem
from rmatics.model.run import Run
from rmatics.model.user import SimpleUser
from rmatics.view.problem.serializers.run import RunSchema

from rmatics.utils.exceptions import (
    ProblemNotFound,
)
from rmatics.utils.validate import (
    validate_args,
)
from rmatics.view import (
    load_problem,
    load_statement,
    require_auth)
from rmatics.view.problem.serializers.problem import ProblemSchema


def load_problem_or_404(problem_id):
    load_problem(problem_id)
    if not g.problem:
        raise ProblemNotFound


class SubmitApi(MethodView):
    post_args = {
        'lang_id': fields.Integer(required=True),
        'statement_id': fields.Integer(),
    }

    @staticmethod
    def check_file_restriction(file, max_size_kb: int = 64) -> bytes:
        """ Function for checking submission restricts
            Checks only size (KB less then max_size_kb)
                and that is is not empty (len > 2)
            Raises
            --------
            ValueError if restriction is failed
        """
        max_size = max_size_kb * 1024
        file_bytes: bytes = file.read(max_size)
        if len(file_bytes) == max_size:
            raise ValueError('Submission should be less than 64Kb')
        # TODO: 4 это прото так, что такое путой файл для ejudje?
        if len(file_bytes) < 4:
            raise ValueError('Submission shouldn\'t be empty')

        return file_bytes

    @require_auth
    def post(self, problem_id: int):
        args = parser.parse(self.post_args)

        language_id = args['lang_id']
        statement_id = args.get('statement_id')
        user_id = g.user.id
        file = parser.parse_files(request, 'file', 'file')

        problem = db.session.query(EjudgeProblem).get(problem_id)
        if not problem:
            raise NotFound('Problem with this id is not found')

        try:
            text = self.check_file_restriction(file)
        except ValueError as e:
            raise BadRequest(e.args[0])
        source_hash = Run.generate_source_hash(text)

        duplicate = db.session.query(Run).filter(Run.user_id == user_id) \
            .filter(Run.problem_id == problem_id) \
            .filter(Run.source_hash == source_hash) \
            .order_by(Run.create_time.desc()).first()
        if duplicate is not None:
            raise BadRequest('Source file is duplicate of your previous submission')

        # TODO: разобраться, есть ли там constraint на statement_id
        run = Run(
            user_id=user_id,
            problem=problem,
            problem_id=problem_id,
            statement_id=statement_id,
            ejudge_contest_id=problem.ejudge_contest_id,
            ejudge_language_id=language_id,
            ejudge_status=98,  # compiling
            source_hash=source_hash,
        )

        db.session.add(run)
        db.session.flush()
        db.session.refresh(run)
        db.session.commit()

        run.update_source(text)

        ejudge_url = current_app.config['EJUDGE_NEW_CLIENT_URL']
        submit = queue_submit(run.id, user_id, ejudge_url)

        return jsonify({
            'last_get_id': get_last_get_id(),
            'submit': submit.serialize()
        })


class TrustedSubmitApi(MethodView):
    post_args = {
        'lang_id': fields.Integer(required=True),
        'statement_id': fields.Integer(),
        'user_id': fields.Integer(required=True),
    }

    @staticmethod
    def check_file_restriction(file, max_size_kb: int = 64) -> bytes:
        """ Function for checking submission restricts
            Checks only size (KB less then max_size_kb)
                and that is is not empty (len > 2)
            Raises
            --------
            ValueError if restriction is failed
        """
        max_size = max_size_kb * 1024
        file_bytes: bytes = file.read(max_size)
        if len(file_bytes) == max_size:
            raise ValueError('Submission should be less than 64Kb')
        # TODO: 4 это прото так, что такое путой файл для ejudje?
        if len(file_bytes) < 4:
            raise ValueError('Submission shouldn\'t be empty')

        return file_bytes

    def post(self, problem_id: int):
        args = parser.parse(self.post_args)

        language_id = args['lang_id']
        statement_id = args.get('statement_id')
        user_id = args.get('user_id')
        file = parser.parse_files(request, 'file', 'file')

        problem = db.session.query(EjudgeProblem).get(problem_id)
        if not problem:
            raise NotFound('Problem with this id is not found')

        try:
            text = self.check_file_restriction(file)
        except ValueError as e:
            raise BadRequest(e.args[0])
        source_hash = Run.generate_source_hash(text)

        duplicate = db.session.query(Run).filter(Run.user_id == user_id) \
            .filter(Run.problem_id == problem_id) \
            .filter(Run.source_hash == source_hash) \
            .order_by(Run.create_time.desc()).first()
        if duplicate is not None:
            raise BadRequest('Source file is duplicate of your previous submission')

        # TODO: разобраться, есть ли там constraint на statement_id
        run = Run(
            user_id=user_id,
            problem=problem,
            problem_id=problem_id,
            statement_id=statement_id,
            ejudge_contest_id=problem.ejudge_contest_id,
            ejudge_language_id=language_id,
            ejudge_status=98,  # compiling
            source_hash=source_hash,
        )

        db.session.add(run)
        db.session.flush()
        db.session.refresh(run)
        db.session.commit()

        run.update_source(text)

        ejudge_url = current_app.config['EJUDGE_NEW_CLIENT_URL']
        submit = queue_submit(run.id, user_id, ejudge_url)

        return jsonify({
            'last_get_id': get_last_get_id(),
            'submit': submit.serialize()
        })


class ProblemApi(MethodView):
    def get(self, problem_id: int):
        problem = db.session.query(EjudgeProblem).get(problem_id)
        if not problem:
            raise NotFound('Problem with this id is not found')

        if not problem.sample_tests:
            schema = ProblemSchema(exclude=['sample_tests_json'])
        else:
            schema = ProblemSchema()

        data = schema.dump(problem)
        return jsonify({'result': 'success', 'data': data.data})


@validate_args({
    'statement_id': lambda statement_id: statement_id is None or int(statement_id)
})
def problem_runs(problem_id):
    load_problem_or_404(problem_id)

    runs = g.problem.runs
    if 'statement_id' in request.args:
        statement_id = int(request.args['statement_id'])
        load_statement(statement_id, silent=False)
        runs = runs.filter_by(statement_id=statement_id)
    elif g.get('user', None):
        runs = runs.filter_by(user_id=g.user.id)
    else:
        return jsonify({})

    return jsonify({
        run.id: run.serialize()
        for run in runs.all()
    })


get_args = {
    'user_id': fields.Integer(),
    'group_id': fields.Integer(),
    'lang_id': fields.Integer(),
    'status_id': fields.Integer(),
    'statement_id': fields.Integer(),
    'count': fields.Integer(default=10, missing=10),
    'page': fields.Integer(required=True),
    'from_timestamp': fields.Integer(),  # Может быть -1, тогда не фильтруем
    'to_timestamp': fields.Integer(),  # Может быть -1, тогда не фильтруем
}


# TODO: only teacher
class ProblemSubmissionsFilterApi(MethodView):
    """ View for getting problem submissions

        Possible filters
        ----------------
        from_timestamp: timestamp
        to_timestamp: timestamp
        group_id: int
        user_id: int
        lang_id: int
        status_id: int
        statement_id: int

        Returns
        --------
        'result': success | error
        'data': [Run]
        'metadata': {count: int, page_count: int}
    """
    def get(self, problem_id: int):
        args = parser.parse(get_args, request)
        user_id = args.get('user_id')
        group_id = args.get('group_id')
        lang_id = args.get('lang_id')
        status_id = args.get('status_id')
        statement_id = args.get('statement_id')
        from_timestamp = args.get('from_timestamp')
        to_timestamp = args.get('to_timestamp')

        per_page_count = args.get('count')
        page = args.get('page')

        try:
            from_timestamp = from_timestamp and from_timestamp != -1 and \
                datetime.datetime.fromtimestamp(from_timestamp / 1_000)
            to_timestamp = to_timestamp and to_timestamp != -1 and \
                datetime.datetime.fromtimestamp(to_timestamp / 1_000)
        except (OSError, OverflowError, ValueError):
            raise BadRequest('Bad timestamp data')

        query = db.session.query(Run, SimpleUser, Problem) \
                          .join(SimpleUser, SimpleUser.id == Run.user_id) \
                          .join(Problem, Problem.id == Run.problem_id) \
                          .filter(Run.problem_id == problem_id)

        if group_id:
            query = query.join(UserGroup, UserGroup.user_id == SimpleUser.id)\
                         .filter(UserGroup.group_id == group_id)
        if user_id:
            query = query.filter(Run.user_id == user_id)
        if lang_id:
            query = query.filter(Run.ejudge_language_id == lang_id)
        if status_id:
            query = query.filter(Run.ejudge_status == status_id)
        if statement_id:
            query = query.filter(Run.statement_id == statement_id)
        if from_timestamp:
            query = query.filter(Run.create_time > from_timestamp)
        if to_timestamp:
            query = query.filter(Run.create_time < to_timestamp)

        result = query.paginate(page=page, per_page=per_page_count, max_per_page=100)

        runs = []
        for run, user, problem in result.items:
            run.user = user
            run.problem = problem
            runs.append(run)

        metadata = {
            'count': result.total,
            'page_count': result.pages
        }

        schema = RunSchema(many=True)
        data = schema.dump(runs)

        return jsonify({'result': 'success', 'data': data.data, 'metadata': metadata})


# @view_config(route_name='problem.standings', renderer='json', request_method='GET')
# @validate_matchdict(IntParam('problem_id', required=True))
# @with_context
# def problem_standings(request, context):
#     if not context.problem:
#         raise ProblemNotFound
#
#     problem = context.problem
#
#     if problem.standings is None:
#         standings = ProblemStandings.create(problem_id=problem.id)
#     else:
#         standings = problem.standings
#
#     return standings.serialize(context)
