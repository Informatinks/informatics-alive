from flask import Flask


def create_app(config=None):
    app = Flask(__name__)

    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_envvar('RMATICS_SETTINGS', silent=True)
    if config:
        app.config.update(config)
    app.url_map.strict_slashes = False

    # Model
    from rmatics.model.base import db
    db.init_app(app)

    # MongoDB
    from rmatics.model.base import mongo
    mongo.init_app(app)

    # Redis
    from rmatics.model.base import redis
    redis.init_app(app)

    # View
    from rmatics.view import (
        handle_api_exception,
        load_user,
    )
    from werkzeug.exceptions import HTTPException
    app.register_error_handler(HTTPException, handle_api_exception)
    app.before_request(load_user)

    from rmatics.view.user.auth import auth
    from rmatics.view.bootstrap import bootstrap
    from rmatics.view.course import course_blueprint
    from rmatics.view.user.group import group
    from rmatics.view.user.group_invite import group_invite
    from rmatics.view.user.notification import notification
    from rmatics.view.problem.route import problem_blueprint
    from rmatics.view.protocol import protocol
    from rmatics.view.course.statement import statement_blueprint
    from rmatics.view.problem.submit import submit
    from rmatics.view.user.user import user
    app.register_blueprint(auth)
    app.register_blueprint(bootstrap)
    app.register_blueprint(course_blueprint)
    app.register_blueprint(group)
    app.register_blueprint(group_invite)
    app.register_blueprint(notification)
    app.register_blueprint(problem_blueprint)
    app.register_blueprint(protocol)
    app.register_blueprint(statement_blueprint)
    app.register_blueprint(submit)
    app.register_blueprint(user)

    # Utils
    from rmatics.utils import url_encoder
    url_encoder.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)
