from flask import (
    g,
    jsonify,
    request,
    Blueprint,
)
from sqlalchemy import and_

from rmatics.model import db
from rmatics.model.group import (
    Group,
    UserGroup,
)
from rmatics.model.group_invite import GroupInvite
from rmatics.utils.exceptions import GroupNotFound
from rmatics.view import require_auth


group = Blueprint('group', __name__, url_prefix='/group')


@group.route('/<int:group_id>')
def group_get(group_id):
    try:
        group = db.session.query(Group).filter(
            and_(
                Group.id == group_id,
                Group.visible == True
            )
        ).one()
    except Exception:
        raise GroupNotFound

    return jsonify(group.serialize())


@group.route('/')
def group_search():
    name = request.args.get('name', '')
    groups = db.session.query(Group) \
        .filter(
            and_(
                Group.name.contains(name),
                Group.visible == True
            )
        ) \
        .order_by(Group.id) \
        .limit(5) \
        .all()
    result = {
        group.id: group.serialize()
        for group in groups
    }
    return jsonify(result)


@group.route('/join/<group_invite_url>', methods=['POST'])
@require_auth
def group_join_by_invite(group_invite_url):
    group_invite = GroupInvite.get_by_url(group_invite_url)
    user_group = UserGroup.create_if_not_exists(
        user_id=g.user.id,
        group_id=group_invite.group_id
    )
    joined = bool(user_group)
    if joined:
        db.session.add(user_group)
    response = {
        'joined': joined,
        'redirect': group_invite.redirect
    }
    return jsonify(response)
