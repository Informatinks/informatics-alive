from gevent import monkey
monkey.patch_all()

from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_envvar('RMATICS_SETTINGS', silent=True)
    if config:
        app.config.update(config)
    app.url_map.strict_slashes = False

    # SocketIO
    from rmatics.websocket import socket
    socket.init_app(
        app,
        # async_mode='gevent_uwsgi',
        message_queue=app.config.get('REDIS_URL'),
    )

    # Model
    from rmatics.model import db
    from rmatics.model.action import Action
    from rmatics.model.book import Book
    from rmatics.model.comment import Comment
    from rmatics.model.contests_statistic import ContestsStatistic
    from rmatics.model.course import Course
    from rmatics.model.course_module import CourseModule
    from rmatics.model.course_section import CourseSection
    from rmatics.model.ejudge_contest import EjudgeContest
    from rmatics.model.ejudge_run import EjudgeRun
    from rmatics.model.group import Group, UserGroup
    from rmatics.model.group_invite import GroupInvite
    from rmatics.model.hint import Hint
    from rmatics.model.ideal_solution import Ideal
    from rmatics.model.log import Log
    from rmatics.model.monitor import Monitor
    from rmatics.model.participant import Participant
    from rmatics.model.problem import (
        EjudgeProblem,
        Problem,
    )
    from rmatics.model.pynformatics_run import PynformaticsRun
    from rmatics.model.recommendation import Recommendation
    from rmatics.model.role import (
        Context,
        Role,
        RoleAssignment,
    )
    from rmatics.model.run import Run
    from rmatics.model.standings import ProblemStandings, StatementStandings
    from rmatics.model.stars import Stars
    from rmatics.model.statement import Statement, StatementUser, StatementProblem
    from rmatics.model.user import SimpleUser, User, PynformaticsUser
    from rmatics.model.user_oauth_provider import UserOAuthProvider

    from rmatics.model.label import Label
    from rmatics.model.resource import Resource

    db.init_app(app)

    # MongoDB
    from rmatics.model import mongo
    mongo.init_app(app)

    # Redis
    from rmatics.model import redis
    redis.init_app(app)

    # View
    with app.app_context():
        from rmatics.view import (
            handle_api_exception,
            load_user,
        )
        from rmatics.utils.exceptions import BaseApiException
        app.register_error_handler(BaseApiException, handle_api_exception)
        app.before_request(load_user)

        from rmatics.view.auth import auth
        from rmatics.view.bootstrap import bootstrap
        from rmatics.view.course import course
        from rmatics.view.group import group
        from rmatics.view.group_invite import group_invite
        from rmatics.view.notification import notification
        from rmatics.view.problem import problem
        from rmatics.view.protocol import protocol
        from rmatics.view.statement import statement
        from rmatics.view.submit import submit
        from rmatics.view.user import user
        app.register_blueprint(auth)
        app.register_blueprint(bootstrap)
        app.register_blueprint(course)
        app.register_blueprint(group)
        app.register_blueprint(group_invite)
        app.register_blueprint(notification)
        app.register_blueprint(problem)
        app.register_blueprint(protocol)
        app.register_blueprint(statement)
        app.register_blueprint(submit)
        app.register_blueprint(user)

    # Utils
    from rmatics.utils import url_encoder
    url_encoder.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)