from flask import jsonify
from sqlalchemy.orm import Load

from rmatics import db
from rmatics.model import CourseModule, Problem, StatementProblem

DEFAULT_MESSAGE = (
    'Oops! An error happened. We are already '
    'trying to resolve the problem!'
)


def handle_api_exception(api_exception):
    code = getattr(api_exception, 'code', 500)
    if not isinstance(code, int):
        code = 500
    message = getattr(api_exception, 'description', DEFAULT_MESSAGE)
    response = jsonify(status='error', code=code, error=message)
    response.status_code = code
    return response


def get_problems_by_course_module(contest_id) -> list:
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
        mdl_statements_problems_correlation.statement_id = 928
    ORDER BY
        mdl_statements_problems_correlation.rank 
    """

    problems_statement_problems = db.session.query(Problem, StatementProblem) \
        .join(StatementProblem, StatementProblem.problem_id == Problem.id) \
        .filter(StatementProblem.statement_id == statement.id) \
        .options(Load(Problem).load_only('id', 'name'))\
        .options(Load(StatementProblem).load_only('rank'))

    problems = []
    # Yes it is ugly but I think its better than rewrite query
    for problem, sp in problems_statement_problems.all():
        problem.rank = sp.rank
        problems.append(problem)

    return problems
