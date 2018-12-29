from logging.config import dictConfig

from flask import Flask
from werkzeug.exceptions import HTTPException

from rmatics.model.base import db
from rmatics.model.base import mongo
from rmatics.model.base import redis
from rmatics.view import handle_api_exception, load_user
from rmatics.view.bootstrap import bootstrap
from rmatics.view.centrifugo import centrifugo_client
from rmatics.view.course import course_blueprint
from rmatics.view.course.statement import statement_blueprint
from rmatics.view.problem.route import problem_blueprint
from rmatics.view.problem.submit import submit
from rmatics.view.protocol import protocol
from rmatics.view.user.auth import auth
from rmatics.view.user.group import group
from rmatics.view.user.group_invite import group_invite
from rmatics.view.user.notification import notification
from rmatics.view.user.user import user
from rmatics.utils import url_encoder
from rmatics import cli


def create_app(config=None):

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'stdout': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['stdout']
        }
    })

    app = Flask(__name__)

    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_envvar('RMATICS_SETTINGS', silent=True)
    if config:
        app.config.update(config)
    app.url_map.strict_slashes = False

    db.init_app(app)
    mongo.init_app(app)
    redis.init_app(app)

    # Centrifugo
    cent_url = app.config.get('CENTRIFUGO_URL')
    cent_api_key = app.config.get('CENTRIFUGO_API_KEY')
    centrifugo_client.init_app(cent_url, cent_api_key)

    app.register_error_handler(HTTPException, handle_api_exception)
    app.before_request(load_user)

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

    app.cli.add_command(cli.test)

    # Utils
    url_encoder.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)
