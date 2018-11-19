from flask import (
    g,
    jsonify,
    Blueprint,
)

from rmatics.ejudge.submit_queue import (
    get_last_get_id,
    peek_user_submits,
)
from rmatics.view import require_auth

submit = Blueprint('submit', __name__, url_prefix='/submit')


@submit.route('/')
@require_auth
def submit_get():
    submits = peek_user_submits(user_id=g.user.id)
    return jsonify({
        'last_get_id': get_last_get_id(),
        'submits': {
            submit.id: submit.serialize()
            for submit in submits
        }
    })

