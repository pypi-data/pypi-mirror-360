# ----------------------------------------------------------------------------------------
# Python-Backpack - Pattern Utilities
# Maximiliano Rocamora / maxirocamora@gmail.com
# https://github.com/MaxRocamora/python-backpack
# ----------------------------------------------------------------------------------------
from datetime import datetime, timedelta, timezone
from functools import lru_cache, wraps

from backpack.logger import get_logger

log = get_logger('Python Backpack - Cache')


def timed_lru_cache(seconds: int, maxsize: int = 128):
    """Lru_cache with expiration time.

    Args:
        seconds (int): expiration time in seconds
        maxsize (int): maxsize for lru_cache
    Note:
        Wrapped function can be forced to clear cache with: force_clear=True
        Wrapped function can show log on clear with: show_log=True
    Returns:
        function result

    # * Usage:

        # * Add the decorator to your function

        @timed_lru_cache(seconds=60)
        def my_function():
            return 'Hello World'

        # * to clear the cache, use force_clear=True on the function call
        my_function(force_clear=True)

    """

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize)(func)
        func.lifetime = timedelta(seconds=seconds)
        func.expiration = datetime.now(timezone.utc) + func.lifetime

        @wraps(func)
        def wrapped_func(*args, force_clear: bool = False, show_log: bool = False, **kwargs):
            """Wrapper function for lru_cache with expiration time.

            Args:
                *args: function arguments
                force_clear (bool): forces a clear cache
                show_log (bool): show log on clear
                **kwargs: function keyword arguments
            Returns:
                function result
            """

            if force_clear or datetime.now(timezone.utc) >= func.expiration:
                if show_log:
                    log.debug(f'Cache cleared for {func.__name__}')

                func.cache_clear()
                func.expiration = datetime.now(timezone.utc) + func.lifetime

            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache
