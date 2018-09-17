# import json
# import mock
# from flask import session
# from hamcrest import (
#     assert_that,
#     calling,
#     equal_to,
#     raises,
# )

# from rmatics.model import db
# from rmatics.model.user_oauth_provider import UserOAuthProvider
# from rmatics.testutils import TestCase
# from rmatics.utils.exceptions import AuthOAuthUserNotFound
# from rmatics.view.auth import auth_oauth_login


# class TestView__auth_oauth_login(TestCase):
#     def setUp(self):
#         super(TestView__auth_oauth_login, self).setUp()

#         self.create_users()

#         self.provider = 'some provider'
#         self.code = 'some code'
#         # self.request.json_body = {
#         #     'provider': self.provider,
#         #     'code': self.code,
#         # }

#         self.oauth_id = 'some oauth id'
#         self.user_oauth_provider = UserOAuthProvider(
#             user=self.users[0],
#             provider=self.provider,
#             oauth_id=self.oauth_id,
#         )
#         db.session.add(self.user_oauth_provider)

#     def test_simple(self):
#         with mock.patch('rmatics.view.auth.get_oauth_id', mock.Mock(return_value=self.oauth_id)):
#             with self.app.test_request_context(
#                 data=json.dumps({
#                     'provider': self.provider,
#                     'code': self.code,
#                 })
#             ):
#                 auth_oauth_login()
#                 assert_that(session, equal_to({'user_id': self.users[0].id}))

#     def test_no_oauth_user(self):
#         with mock.patch('rmatics.view.auth.get_oauth_id', mock.Mock(return_value='unknown oauth_id')):
#             with self.app.test_request_context(
#                 data=json.dumps({
#                     'provider': '',
#                     'code': '',
#                 })
#             ):
#                 assert_that(
#                     calling(auth_oauth_login),
#                     raises(AuthOAuthUserNotFound)
#                 )
