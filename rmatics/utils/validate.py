from flask import (
    jsonify,
    request,
)
from functools import wraps
from jsonschema import Draft4Validator

from rmatics.utils.exceptions import BadRequest


def validate_schema(schema):
    validator = Draft4Validator(schema)

    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            json = request.get_json(force=True)
            errors = [error.message for error in validator.iter_errors(json)]
            if errors:
                response = jsonify({
                    'code': 400,
                    'message': errors[0],
                })
                response.status_code = 400
                return response

            return func(*args, **kwargs)
        return wrapped
    return wrapper


def validate(key, validators):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            for arg, validator in validators.items():
                try:
                    validator(getattr(request, key).get(arg))
                except Exception:
                    raise BadRequest
            return func(*args, **kwargs)
        return wrapped
    return wrapper


def validate_args(validators):
    return validate('args', validators)


def validate_form(validators):
    return validate('form', validators)
