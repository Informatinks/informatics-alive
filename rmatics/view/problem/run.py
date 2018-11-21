import io

from flask import send_file, g
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from rmatics.model.base import db
from rmatics.model.run import Run
from rmatics.view import require_auth, require_roles


class SourceApi(MethodView):
    @require_auth
    def get(self, run_id: int):

        user_id = g.user.id

        run = db.session.query(Run).get(run_id)

        if run is None:
            raise NotFound()

        if run.user_id != user_id:
            # TODO: Rewrite permissions
            # This construction raises Forbidden if roles are not allowed
            require_roles('admin', 'teacher')(lambda *_, **__: None)()

        source = run.source

        # TODO: Придумать что-то получше для бинарных submission-ов
        return send_file(io.BytesIO(source),
                         attachment_filename='submission.txt')
