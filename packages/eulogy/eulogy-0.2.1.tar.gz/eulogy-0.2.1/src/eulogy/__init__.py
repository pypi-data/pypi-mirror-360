__version__ = "0.2.1"

import atexit
import functools
import inspect
from typing import List, Optional

from .eulogy import Config as Config
from .eulogy import _Eulogy

eulogy = _Eulogy()


def eulogise(tags: Optional[List] = None):
    """Function decorator to record function calls

    Args:
        tags (Optional[List], optional): An optional list of string data to be
        recorded with the function call. This could be useful in cases where
        multiple runs are being piped to a single file. Defaults to None.
    """

    def decorator(func):
        @functools.wraps(func)
        def add_function_log(*args, **kwargs):
            if not eulogy.config.ignore_functions:
                module = inspect.getmodule(func).__name__
                log = f"Function: {module}.{func.__name__}"
                if tags is not None:
                    joined_tags = ", ".join(tags)
                    log = " ".join([log, "[TAGS]", joined_tags])
                eulogy.add(log)
            return func(*args, **kwargs)

        return add_function_log

    return decorator


atexit.register(eulogy.recite)
