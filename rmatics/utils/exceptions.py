from werkzeug.exceptions import BadRequest, \
    Forbidden, NotFound


# Auth
class AuthWrongUsernameOrPassword(Forbidden):
    description = 'Wrong username or password'


class AuthOAuthUserNotFound(NotFound):
    description = 'No user with this OAuth ID'


class AuthOAuthBadProvider(BadRequest):
    description = 'Unknown OAuth provider'


class UserOAuthIdAlreadyUsed(Forbidden):
    description = 'OAuth ID already in use'


# Course
class CourseNotFound(NotFound):
    description = 'No course with this id'


# Ejudge
class EjudgeError(BadRequest):
    description = 'Ejudge error'


# Group
class GroupNotFound(NotFound):
    description = 'Group not found'


# Problem
class ProblemNotFound(NotFound):
    description = 'No problem with this id'


# Statement
class StatementNotFound(NotFound):
    description = 'No statement with this id'


class StatementNotVirtual(BadRequest):
    description = 'Not a virtual contest'


class StatementCanOnlyStartOnce(Forbidden):
    description = 'Can only start contest once'


class StatementOnlyOneOngoing(Forbidden):
    description = 'Can only have one ongoing contest'


class StatementNothingToFinish(Forbidden):
    description = 'No ongoing virtual contests'


class StatementNotOlympiad(BadRequest):
    description = 'Not an olympiad'


class StatementFinished(Forbidden):
    description = 'Contest already finished'


class StatementNotStarted(Forbidden):
    description = 'Contest not started'


class StatementSettingsValidationError(BadRequest):
    description = 'Invalid settings format'


class StatementPasswordIsWrong(Forbidden):
    description = 'Password is wrong or missing'


# User
class UserNotFound(NotFound):
    description = 'No such user'


# Search
class SearchQueryIsEmpty(BadRequest):
    description = 'Search query is empty'


# Pagination
class PaginationPageOutOfRange(BadRequest):
    description = 'Page number is out of range'


class PaginationPageSizeNegativeOrZero(BadRequest):
    description = 'Page size is negative or zero'


# Run
class RunNotFound(NotFound):
    description = 'Run not found'


class RunAuthorOnly(Forbidden):
    description = 'Only accessible by author or admin'
