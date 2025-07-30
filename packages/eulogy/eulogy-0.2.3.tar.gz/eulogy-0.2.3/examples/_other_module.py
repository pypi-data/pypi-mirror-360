import functools

from eulogy import eulogise


def test_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("__ test __")
        return func(*args, **kwargs)

    return wrapper


@eulogise(["thing 1", "thing 2"])
@test_decorator
def test_function():
    return 5
