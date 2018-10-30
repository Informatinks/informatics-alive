import functools
import warnings


def deprecated(new_name=None):
    """Deprecate something."""

    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            if new_name:
                message = (
                    f'{func.__module__}.{func.__name__} is deprecated. Please '
                    f'replace it by {new_name}'
                )
            else:
                message = (
                    f'{func.__module__}.{func.__name__} is deprecated, but it '
                    f'doesn\'t have any replacement yet.'
                )

            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)

        return new_func

    return decorator


def do_not_execute(return_value=None, raised_exception=None):

    def decorator(func):
        @functools.wraps(func)
        def new_func(*_, **__):
            if raised_exception:
                raise raised_exception
            return return_value
        return new_func

    return decorator
