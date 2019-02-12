from logging.config import dictConfig

from flask import Flask
from werkzeug.exceptions import HTTPException

from rmatics.model.base import db
from rmatics.model.base import mongo
from rmatics.model.base import redis
from rmatics.plugins import monitor_cacher
from rmatics.view import handle_api_exception
from rmatics.view.centrifugo import centrifugo_client
from rmatics.view.monitors.route import monitor_blueprint
from rmatics.view.problem.route import problem_blueprint
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

    monitor_cacher.init_app(app, redis, period=30*60, autocommit=False)

    # Centrifugo
    cent_url = app.config.get('CENTRIFUGO_URL')
    cent_api_key = app.config.get('CENTRIFUGO_API_KEY')
    centrifugo_client.init_app(cent_url, cent_api_key)

    app.register_error_handler(HTTPException, handle_api_exception)

    app.register_blueprint(problem_blueprint)
    app.register_blueprint(monitor_blueprint)

    app.cli.add_command(cli.test)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)
