from flask import (
    g,
    jsonify,
    session,
)
from functools import wraps
from sqlalchemy import exists, join

from rmatics.model import db
from rmatics.model.course import Course
from rmatics.model.problem import EjudgeProblem
from rmatics.model.role import (
    Role,
    RoleAssignment,
)
from rmatics.model.statement import Statement
from rmatics.model.user import SimpleUser
from werkzeug.exceptions import Forbidden, Unauthorized
from rmatics.utils.exceptions import (
    CourseNotFound,
    StatementNotFound,
    ProblemNotFound,
)


DEFAULT_MESSAGE = (
    'Oops! An error happened. We are already '
    'trying to resolve the problem!'
)


def handle_api_exception(api_exception):
    code = getattr(api_exception, 'code', 500)
    message = getattr(api_exception, 'description', DEFAULT_MESSAGE)
    response = jsonify(result='error', code=code, message=message)
    response.status_code = code
    return response


def load_user():
    user_id = session.get('user_id')
    user = db.session.query(SimpleUser).filter_by(id=user_id).one_or_none()
    g.user = user


def load_problem(problem_id, silent=True):
    problem = db.session.query(EjudgeProblem).filter_by(id=problem_id).first()
    g.problem = problem
    if not silent and not problem:
        raise ProblemNotFound


def load_statement(statement_id, silent=True):
    statement = db.session.query(Statement).filter_by(id=statement_id).one_or_none()
    g.statement = statement
    if not silent and not statement:
        raise StatementNotFound


def load_course(course_id, silent=True):
    course = db.session.query(Course).filter_by(id=course_id).first()
    g.course = course
    if not silent and not course:
        raise CourseNotFound


def require_auth(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if not g.get('user', None):
            raise Unauthorized
        return func(*args, **kwargs)
    return wrapped


def require_roles(*roles):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if not getattr(g, 'user', None):
                raise Unauthorized

            role_assignment_exists = db.session.query(
                exists() \
                    .select_from(join(RoleAssignment, Role)) \
                    .where(RoleAssignment.user_id == g.user.id) \
                    .where(Role.shortname.in_(roles))
            ).scalar()

            if not role_assignment_exists:
                raise Forbidden

            return func(*args, **kwargs)
        return wrapped
    return wrapper


# @current_app.before_request
# def load_problem():
#     print('load problem')
#     for l in vars(request).keys():
#         print(l)
#     print(request.view_args)
#     print(request.args)
