from flask import jsonify


DEFAULT_MESSAGE = (
    'Oops! An error happened. We are already '
    'trying to resolve the problem!'
)


def handle_api_exception(api_exception):
    code = getattr(api_exception, 'code', 500)
    if not isinstance(code, int):
        code = 500
    message = getattr(api_exception, 'description', DEFAULT_MESSAGE)
    response = jsonify(status='error', code=code, message=message)
    response.status_code = code
    return response
