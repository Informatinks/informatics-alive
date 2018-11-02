from flask import (
    g,
    jsonify,
    request,
    Blueprint,
)
from sqlalchemy import and_

from rmatics.model import db
from rmatics.model.course_module import CourseModule
from rmatics.model.standings import StatementStandings
from rmatics.view import (
    load_statement,
    require_auth,
    require_roles,
)
from rmatics.utils.exceptions import StatementNotFound
from rmatics.utils.validate import validate_args


statement = Blueprint('statement', __name__, url_prefix='/statement')


def load_statement_or_404(statement_id):
    load_statement(statement_id)
    if not g.statement:
        raise StatementNotFound


@statement.route('/<int:statement_id>')
def statement_get(statement_id):
    load_statement_or_404(statement_id)
    return jsonify(g.statement.serialize())


@statement.route('/<int:statement_id>/set_settings', methods=['POST'])
@require_roles('admin')
def statement_set_settings(statement_id):
    load_statement_or_404(statement_id)
    g.statement.set_settings(request.get_json())
    return jsonify(g.statement.serialize())


@statement.route('/<int:statement_id>/start_virtual', methods=['POST'])
@require_auth
def statement_start_virtual(statement_id):
    load_statement_or_404(statement_id)
    password = (request.get_json() or {}).get('password', '')
    participant = g.statement.start_virtual(
        user=g.user,
        password=password,
    )
    return jsonify(participant.serialize())


@statement.route('/<int:statement_id>/finish_virtual', methods=['POST'])
@require_auth
def statement_finish_virtual(statement_id):
    load_statement_or_404(statement_id)
    participant = g.statement.finish_virtual(g.user)
    return jsonify(participant.serialize())


@statement.route('/<int:statement_id>/start', methods=['POST'])
@require_auth
def statement_start(statement_id):
    load_statement_or_404(statement_id)
    password = (request.get_json() or {}).get('password', '')
    participant = g.statement.start(
        user=g.user,
        password=password,
    )
    return jsonify(participant.serialize())


@statement.route('/<int:statement_id>/finish', methods=['POST'])
@require_auth
def statement_finish(statement_id):
    load_statement_or_404(statement_id)
    participant = g.statement.finish(g.user)
    return jsonify(participant.serialize())


@statement.route('/')
@validate_args({
    'course_module_id': int,
})
def statement_get_by_module():
    course_module_id = int(request.args['course_module_id'])
    course_module = db.session.query(CourseModule) \
        .filter(
            and_(
                CourseModule.id == course_module_id,
                CourseModule.module == 19
            )
        ) \
        .first()

    if not course_module:
        raise StatementNotFound

    load_statement(course_module.instance.id)
    if not g.statement:
        raise StatementNotFound

    return jsonify(g.statement.serialize())


@statement.route('/<int:statement_id>/standings')
@validate_args({
    'group_id': lambda group_id: group_id is None or int(group_id)
})
def statement_standings(statement_id):
    load_statement_or_404(statement_id)

    if g.statement.standings is None:
        standings = StatementStandings.create(statement_id=g.statement.id)
    else:
        standings = g.statement.standings

    group_id = None
    if 'group_id' in request.args:
        group_id = int(request.args['group_id'])

    return jsonify(
        standings.serialize(
            group_id=group_id,
        )
    )
