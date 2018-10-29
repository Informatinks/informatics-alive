import datetime

from flask import (
    current_app,
    g,
    jsonify,
    request,
    Blueprint,
)

from rmatics.ejudge.submit_queue import (
    get_last_get_id,
    queue_submit,
)
from rmatics.model import db
from rmatics.model.run import Run

from rmatics.model.standings import ProblemStandings
# from rmatics.view.utils import *
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


problem = Blueprint('problem', __name__, url_prefix='/problem')


def load_problem_or_404(problem_id):
    load_problem(problem_id)
    if not g.problem:
        raise ProblemNotFound


@problem.route('/<int:problem_id>/submit_v2', methods=['POST'])
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


@problem.route('/trusted/<int:problem_id>/submit_v2', methods=['POST'])
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

    run = Run(
        user_id=user_id,
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
    db.session.refresh(run)

    text = file.read()
    run.update_source(text)

    submit = queue_submit(run.id, user_id, ejudge_url)

    return jsonify({
        'last_get_id': get_last_get_id(),
        'submit': submit.serialize()
    })


@problem.route('/<int:problem_id>')
def problem_get(problem_id):
    load_problem_or_404(problem_id)
    return jsonify(g.problem.serialize())


@problem.route('/<int:problem_id>/runs')
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
