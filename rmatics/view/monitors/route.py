from flask import Blueprint

from rmatics.view.monitors.monitor import MonitorAPIView

monitor_blueprint = Blueprint('monitor', __name__, url_prefix='/monitor')

monitor_blueprint.add_url_rule('/', methods=('GET', ),
                               view_func=MonitorAPIView.as_view('crud'))
