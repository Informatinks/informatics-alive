import functools
from typing import Callable

from rmatics.utils.cacher.cacher import Cacher
from rmatics.utils.cacher.locker import RedisLocker


class DeferredWrapper:
    """
    Wraps function after calling .wraps(wrapper: Callable) only
    """
    def __init__(self, f):
        self.f = f

    def wrap(self, wrapper: Callable):
        self.f = wrapper(self.f)

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


class FlaskCacher:
    """ Wrapper for Flask and Cacher integration
    Usage:
    ------
        cacher = FlaskCacher(prefix='my_cache')
        ...
        @cacher
        def cache_me_pls(problem_ids=None):
            ...
        ...

        def create_app():
            app = Flask()
            store = Redis(app)
            cacher.init_app(app, store, period=30*60)
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        self._app = None
        self._instance = None
        self._deferred_wrappers = []

    def init_app(self, app, store, **kwargs):
        # TODO: Сохранить в плагины
        self._app = app
        self._kwargs.update(kwargs)
        redis_url = app.config['REDIS_URL']
        locker = RedisLocker(redis_url)
        self._instance = Cacher(store, locker, *self._args, **self._kwargs)

        for wrapper in self._deferred_wrappers:
            wrapper.wrap(self._instance)
        # We should clear DeferredWrapper's list to avoid second wrapping
        # If someone calls init_app twice
        self._deferred_wrappers.clear()

    def invalidate_any_of(self, func, **kwargs):
        res = self._instance.invalidate_any_of(func, **kwargs)
        if not res:
            msg = f'Function Cacher.invalidate_any_of was called' \
                   'for function {func.__name__} but could not invalidate cache' \
                   'with current args.'
            self._app.logger.warning(msg)

    def invalidate_all_of(self, func, **kwargs):
        res = self._instance.invalidate_all_of(func, **kwargs)
        if not res:
            msg = f'Function Cacher.invalidate_all_of was called' \
                   'for function {func.__name__} but could not invalidate cache' \
                   'with current args.'
            self._app.logger.warning(msg)

    def __call__(self, f: Callable):
        # We use deferred wrapping because when decorator called
        # We did not have self._instance: we did not call init_app yet
        wrapper = functools.wraps(f)(DeferredWrapper(f))
        self._deferred_wrappers.append(wrapper)
        return wrapper

    def __getattr__(self, item):
        return getattr(self._instance, item)
