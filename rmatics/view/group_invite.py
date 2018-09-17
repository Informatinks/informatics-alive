from flask import (
    g,
    jsonify,
    Blueprint,
)

from rmatics.model import db
from rmatics.model.group_invite import GroupInvite
from rmatics.view import require_auth


group_invite = Blueprint('group_invite', __name__, url_prefix='/group_invite')


@group_invite.route('/')
@require_auth
def group_invite_get():
    group_invites = db.session.query(GroupInvite) \
        .filter_by(creator_id=g.user.id) \
        .all()
    return jsonify([
        group_invite.serialize()
        for group_invite in group_invites
    ])
