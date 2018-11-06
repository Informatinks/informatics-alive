import datetime

from flask import (
    current_app,
    g,
    jsonify,
    request,
    Blueprint,
)
from sqlalchemy import func
from werkzeug.exceptions import BadRequest
from flask.views import MethodView
from rmatics.ejudge.submit_queue import (
    get_last_get_id,
    queue_submit,
)
from webargs.flaskparser import parser
from marshmallow import fields
from rmatics.model import db
from rmatics.model.problem import Problem
from rmatics.model.run import Run
from rmatics.model.user import SimpleUser
from rmatics.view.serializers import RunSchema

from rmatics.utils.exceptions import (
    ProblemNotFound,
)
from rmatics.utils.validate import (
    validate_args,
    validate_form,
)
from rmatics.view import (
    load_problem,
    load_statement,
    require_auth)


problem_blueprint = Blueprint('problem', __name__, url_prefix='/problem')


def load_problem_or_404(problem_id):
    load_problem(problem_id)
    if not g.problem:
        raise ProblemNotFound


@problem_blueprint.route('/<int:problem_id>/submit_v2', methods=['POST'])
@require_auth
@validate_form({
    'lang_id': int,
    'statement_id': lambda statement_id: statement_id is None or int(statement_id)
})
def problem_submit_v2(problem_id):
    load_problem(problem_id)
    language_id = int(request.form['lang_id'])
    file = request.files['file']
    ejudge_url = current_app.config['EJUDGE_NEW_CLIENT_URL']
    statement_id = request.form.get('statement_id')
    if statement_id:
        statement_id = int(statement_id)

    # if language_id not in context.get_allowed_languages():
    #     raise Forbidden(f'Language id "{language_id}" is not allowed')

    run = Run(
        user_id=g.user.id,
        problem=g.problem,
        problem_id=problem_id,
        statement_id=statement_id,
        create_time=datetime.datetime.now(),
        ejudge_contest_id=g.problem.ejudge_contest_id,
        ejudge_language_id=language_id,
        ejudge_status=98,  # compiling
    )

    db.session.add(run)
    db.session.flush()

    # TODO: different encodings + exception handling
    text = file.read()
    run.update_source(text)

    submit = queue_submit(run.id, g.user.id, ejudge_url)

    return jsonify({
        'last_get_id': get_last_get_id(),
        'submit': submit.serialize()
    })


@problem_blueprint.route('/trusted/<int:problem_id>/submit_v2', methods=['POST'])
@validate_form({
    'lang_id': int,
    'statement_id': lambda statement_id: statement_id is None or int(statement_id),
    'user_id': int,
})
def trusted_problem_submit_v2(problem_id):
    load_problem(problem_id)
    language_id = int(request.form['lang_id'])
    file = request.files['file']
    ejudge_url = current_app.config['EJUDGE_NEW_CLIENT_URL']
    statement_id = request.form.get('statement_id')
    if statement_id:
        statement_id = int(statement_id)

    user_id = int(request.form['user_id'])

    text = file.read()
    try:
        run = Run.create(
            text,
            user_id=user_id,
            problem=g.problem,
            problem_id=problem_id,
            statement_id=statement_id,
            ejudge_contest_id=g.problem.ejudge_contest_id,
            ejudge_language_id=language_id,
            ejudge_status=98,  # compiling
        )
    except ValueError:
        raise BadRequest('Source file is duplicate of your previous submission')

    submit = queue_submit(run.id, user_id, ejudge_url)

    return jsonify({
        'last_get_id': get_last_get_id(),
        'submit': submit.serialize()
    })


@problem_blueprint.route('/<int:problem_id>')
def problem_get(problem_id):
    load_problem_or_404(problem_id)
    return jsonify(g.problem.serialize())


@problem_blueprint.route('/<int:problem_id>/runs')
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
    'page': fields.Integer(required=True),  # TODO: required: True
    'from_timestamp': fields.Integer(),  # Может быть -1, тогда не фильтруем
    'to_timestamp': fields.Integer(),  # Может быть -1, тогда не фильтруем
}


# TODO: only teacher
class ProblemSubmissions(MethodView):
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
        # group_id= args.get('group_id')  # TODO: Фильтрации по группам нет
        lang_id = args.get('lang_id')
        status_id = args.get('status_id')
        statement_id = args.get('statement_id')
        from_timestamp = args.get('from_timestamp')
        to_timestamp = args.get('to_timestamp')

        per_page_count = args.get('count')
        per_page_count = per_page_count if per_page_count <= 100 else 100
        page = args.get('page')

        try:
            from_timestamp = from_timestamp and from_timestamp != -1 and \
                datetime.datetime.fromtimestamp(from_timestamp / 1_000)
            to_timestamp = to_timestamp and to_timestamp != -1 and \
                datetime.datetime.fromtimestamp(to_timestamp / 1_000)
        except (OSError, OverflowError):
            raise BadRequest('Bad timestamp data')

        query = db.session.query(Run, SimpleUser, Problem, func.count()) \
                          .join(SimpleUser, SimpleUser.id == Run.user_id) \
                          .join(Problem, Problem.id == Run.problem_id) \
                          .filter(Run.problem_id == problem_id).group_by(Run.id)
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

        query = query.offset((page - 1) * per_page_count).limit(per_page_count)

        runs = []
        count = 0
        for run, user, problem, cnt in query.all():
            run.user = user
            run.problem = problem
            runs.append(run)
            count += cnt

        metadata = {
            'count': count,
            'page_count': count // per_page_count + 1
        }

        schema = RunSchema(many=True)
        data = schema.dump(runs)

        return jsonify({'result': 'success', 'data': data.data, 'metadata': metadata})


problem_blueprint.add_url_rule('/<int:problem_id>/submissions/', methods=('GET', ),
                               view_func=ProblemSubmissions.as_view('problem_submissions'))


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
