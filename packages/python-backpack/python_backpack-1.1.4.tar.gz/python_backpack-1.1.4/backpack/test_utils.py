# ----------------------------------------------------------------------------------------
# Python-Backpack - Test Utilities
# Maximiliano Rocamora / maxirocamora@gmail.com
# https://github.com/MaxRocamora/python-backpack
# ----------------------------------------------------------------------------------------
import random
import string
import time

from backpack.logger import get_logger

log = get_logger('Python Backpack - TestUtils')


def random_string(length: str = 10) -> str:
    """Generates a random string of fixed length.

    Args:
        length (int, optional): max string length. Defaults to 10.

    Returns:
        str: random string
    """

    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def time_function_decorator(method: type):
    """Decorator to measure methods execution time."""

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        message = f'{method.__name__!r}  {(te - ts) * 1000:2.2f} ms'
        log.info(message)

        return result

    return timed
