from flask import (
    jsonify,
    g,
    request,
    session,
    Blueprint,
)
from sqlalchemy.orm.exc import NoResultFound


from rmatics.model import db
from rmatics.model.user import User
# from rmatics.model.user_oauth_provider import UserOAuthProvider
from rmatics.utils.exceptions import (
    # AuthOAuthUserNotFound,
    AuthWrongUsernameOrPassword,
)
from rmatics.utils.functions import check_password
# from rmatics.utils.oauth import get_oauth_id
from rmatics.utils.validate import validate_schema
from rmatics.view import (
    require_auth,
    load_user,
)


auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/login', methods=['POST'])
@validate_schema({
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
    },
    'required': ['username', 'password'],
})
def auth_login():
    if not g.user:
        username = request.get_json().get('username')
        password = request.get_json().get('password')
        try:
            user = db.session.query(User).filter_by(username=username).one()
        except NoResultFound:
            raise AuthWrongUsernameOrPassword
        if not check_password(password, user.password_md5):
            raise AuthWrongUsernameOrPassword
    else:
        user = g.user

    session['user_id'] = user.id
    return jsonify(user.serialize())


@auth.route('/logout', methods=['POST'])
@require_auth
def auth_logout():
    session['user_id'] = None
    return jsonify({})


# @auth.route('/oauth_login', methods=['POST'])
# @validate_schema({
#     'type': 'object',
#     'properties': {
#         'provider': {'type': 'string'},
#         'code': {'type': 'string'},
#     },
#     'required': ['provider', 'code'],
# })
# def auth_oauth_login():
#     provider = request.get_json().get('provider')
#     code = request.get_json().get('code')
#     oauth_id = get_oauth_id(provider, code)

#     user_oauth_provider = db.session.query(UserOAuthProvider) \
#         .filter_by(provider=provider) \
#         .filter_by(oauth_id=oauth_id) \
#         .first()

#     if not user_oauth_provider:
#         raise AuthOAuthUserNotFound

#     session['user_id'] = user_oauth_provider.user_id
#     load_user()

#     return jsonify(g.user.serialize())
