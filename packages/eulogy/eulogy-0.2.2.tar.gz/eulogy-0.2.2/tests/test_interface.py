from collections import deque

import pytest

from eulogy import Config, eulogise, eulogy

DEFAULT_CONFIG = Config()


@pytest.fixture(autouse=True)
def reset_eulogy():
    eulogy._epitaph = deque(maxlen=DEFAULT_CONFIG.max_report_length)
    eulogy.set_config(DEFAULT_CONFIG)
    return eulogy


@eulogise()
def _test_function_1():
    return


@eulogise(tags=["a", "b"])
def _test_function_2():
    return


def test_handled_exceptions():
    try:
        int("a")
    except ValueError:
        pass
    assert len(eulogy._epitaph) == 0


def test_manual_reporting():
    eulogy.add("xyz")
    with pytest.raises(ValueError):
        int("a")
    assert "xyz" in eulogy._epitaph[0]
    assert len(eulogy._epitaph) == 1


def test_function_reporting():
    _test_function_1()
    with pytest.raises(ValueError):
        int("a")
    assert "_test_function_1" in eulogy._epitaph[0]
    assert len(eulogy._epitaph) == 1


def test_traceback_reporting():
    try:
        int("a")
    except ValueError:
        eulogy.add_tb()
    assert (
        "ValueError: invalid literal for int() with base 10: 'a'"
        in eulogy._epitaph[0]
    )
    assert len(eulogy._epitaph) == 1


def test_tags():
    _test_function_2()
    try:
        int("a")
    except ValueError:
        pass
    assert "[TAGS] a, b" in eulogy._epitaph[0]
    assert len(eulogy._epitaph) == 1


def test_turn_off_manual():
    config = Config(ignore_manual=True)
    eulogy.set_config(config)
    eulogy.add("Something")
    with pytest.raises(ValueError):
        int("a")
    assert len(eulogy._epitaph) == 0


def test_turn_off_functions():
    config = Config(ignore_functions=True)
    eulogy.set_config(config)
    _test_function_1()
    assert len(eulogy._epitaph) == 0


def test_turn_off_tracebacks():
    config = Config(ignore_tracebacks=True)
    eulogy.set_config(config)
    try:
        int("a")
    except ValueError:
        eulogy.add_tb()
    assert len(eulogy._epitaph) == 0


def test_max_len():
    config = Config(max_report_length=2)
    eulogy.set_config(config)
    _test_function_1()
    _test_function_1()
    _test_function_1()
    _test_function_2()
    assert len(eulogy._epitaph) == 2
    # Make sure truncation order is maintained
    assert "test_function_2" in eulogy._epitaph[-1]
