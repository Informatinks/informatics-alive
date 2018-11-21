from flask import (
    g,
    jsonify,
    request,
    Blueprint,
)

from rmatics.model.base import db
from rmatics.model.ejudge_run import EjudgeRun
from rmatics.model.run import Run
from rmatics.utils.exceptions import RunNotFound
from rmatics.utils.validate import validate_args
from rmatics.websocket import notify_user
from rmatics.websocket.events import RUNS_FETCH

notification = Blueprint('notification', __name__, url_prefix='/notification')


# @view_config(route_name='notification.update_standings', renderer='json')
# @validate_params(
#     IntParam('contest_id', required=True),
#     IntParam('run_id', required=True),
# )
# @with_context
# def notification_update_standings(request, context):
#     contest_id = int(request.params['contest_id'])
#     run_id = int(request.params['run_id'])

#     try:
#         run = DBSession.query(EjudgeRun).filter_by(
#             contest_id=contest_id
#         ).filter_by(
#             run_id=run_id
#         ).one()
#     except Exception:
#         raise RunNotFound

#     # if run.problem.standings:
#     #     run.problem.standings.update(run.user)

#     if (run.pynformatics_run
#             and run.pynformatics_run.statement
#             and run.pynformatics_run.statement.standings
#     ):
#         run.pynformatics_run.statement.standings.update(run)

#     context.user_id = run.user.id
#     notify_user(user_id=run.user.id, runs=[run.serialize(context)])

#     return {}


@notification.route('/update_run')
@validate_args({
    'contest_id': int,
    'run_id': int,
})
def notification_update_run():
    contest_id = int(request.args['contest_id'])
    run_id = int(request.args['run_id'])

    try:
        run = db.session.query(EjudgeRun) \
            .filter_by(contest_id=contest_id) \
            .filter_by(run_id=run_id) \
            .one()
    except Exception:
        raise RunNotFound

    run = Run.sync(
        ejudge_run_id=run_id,
        ejudge_contest_id=contest_id
    )
    db.session.commit()
    db.session.refresh(run)

    g.user = run.user
    notify_user(
        run.user_id,
        RUNS_FETCH,
        {
            'runs': [run.serialize()],
        }
    )

    return jsonify({})
