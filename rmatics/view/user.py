from flask import (
    jsonify,
    request,
    Blueprint,
)

from rmatics.model import db
from rmatics.model.user import User
from rmatics.utils.exceptions import (
    UserOAuthIdAlreadyUsed,
    UserNotFound,
)
from rmatics.utils.validate import validate_schema
from rmatics.view import require_roles


user = Blueprint('user', __name__, url_prefix='/user')


# @view_config(route_name='user.set_oauth_id', renderer='json', request_method='POST')
# @with_context(require_auth=True)
# def user_set_oauth_id(request, context):
#     provider = request.json_body.get('provider')
#     code = request.json_body.get('code')
#     oauth_id = get_oauth_id(provider, code)

#     if DBSession.query(UserOAuthProvider).filter(
#                 UserOAuthProvider.provider == provider
#             ).filter(
#                 UserOAuthProvider.oauth_id == oauth_id
#             ).first():
#         raise UserOAuthIdAlreadyUsed

#     user_oauth_provider = context.user.oauth_ids.filter(UserOAuthProvider.provider == provider).first()
#     if user_oauth_provider:
#         user_oauth_provider.oauth_id = oauth_id
#     else:
#         user_oauth_provider = UserOAuthProvider(
#             user_id=context.user.id,
#             provider=provider,
#             oauth_id=oauth_id,
#         )
#         DBSession.add(user_oauth_provider)
#     return {}


@user.route('/reset_password', methods=['POST'])
@validate_schema({
    'type': 'object',
    'properties': {
        'id': {'type': 'integer'},
    },
    'required': ['id'],
})
@require_roles('admin')
def user_reset_password():
    user_id = request.get_json()['id']

    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        raise UserNotFound

    new_password = user.reset_password()
    return jsonify({
        'id': user.id,
        'password': new_password,
    })
