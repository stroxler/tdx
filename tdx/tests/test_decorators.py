import inspect
import pytest
from ..decorators import (
    error_prefix_from_args, debug, _wrapt_proxy_decorator,
    wraptify
)


# test wraptify tools ---------------

def test_wrapt_proxy_decorator():
    def f(x):
        return 1

    def g(y):
        return 2

    out = _wrapt_proxy_decorator(g)(f)
    assert out(1) == 2
    actual_argspec = inspect.getargspec(out)
    expected_argspec = inspect.ArgSpec(
        args=['x'], varargs=None,
        keywords=None, defaults=None
    )
    assert actual_argspec == expected_argspec


def test_wraptify():
    def double_output(f):
        "Decorator to wrap a function in a doubling operation"
        def wrapped(*args, **kwargs):
            return 2 * f(*args, **kwargs)
        return wrapped

    def f(x, y):
        "my docs for f"
        return x + y

    wraptified_double_output = wraptify(double_output)
    nowrapt = double_output(f)
    assert nowrapt(1, 2) == 6
    assert nowrapt.__doc__ is None
    yeswrapt = wraptified_double_output(f)
    assert yeswrapt(1, 2) == 6
    assert yeswrapt.__doc__ == "my docs for f"


# test the debug decorator ---------------

class MockDebugger(object):
    def __init__(self):
        self.called = False

    def post_mortem(self, tb):
        self.called = True


def test_debug_debugger_not_called_if_no_error():

    mock_debugger = MockDebugger()

    @debug(use_debugger=mock_debugger)
    def f(): return 0

    assert f() == 0
    assert not mock_debugger.called


def test_debug_debugger_not_called_if_debug_False():

    mock_debugger = MockDebugger()

    @debug(False, use_debugger=mock_debugger)
    def f(): raise Exception('error')

    with pytest.raises(Exception):
        f()


def test_debug_debugger_called_if_debug_True_and_raises():

    mock_debugger = MockDebugger()

    @debug(use_debugger=mock_debugger)
    def f(): raise Exception('error')

    f()
    assert mock_debugger.called


# test the error prefix decorators ---------------

def assert_error_with_prefix(prefix, func, *args, **kwargs):
    try:
        print args
        func(*args, **kwargs)
        raise AssertionError("No error raised")
    except Exception as e:
        if not e.args[0].startswith(prefix):
            print "expected prefix %r" % prefix
            print "actual message %r" % e.args[0]
            raise


def test_error_prefix_from_args_no_formatting():

    @error_prefix_from_args("error context")
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context:\nan error",
        f, 1, 2,
    )


def test_error_prefix_from_args_simple_formatting():

    @error_prefix_from_args("error context {x} {y} {z}")
    def f(x, y, z):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context 1 2 3:\nan error",
        f, 1, 2, 3
    )


def test_error_prefix_from_args_formatting_with_defaults():

    @error_prefix_from_args("error context {x} {y} {z}")
    def f(x, y=2, z=2):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context 1 2 3:\nan error",
        f, 1, z=3
    )


def test_error_prefix_from_args_formatting_with_packed_args():

    @error_prefix_from_args("error context {fargs} {fkwargs}")
    def f(*fargs, **fkwargs):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context (1, 2) {'z': 3}:\nan error",
        f, 1, 2, z=3
    )


def test_error_prefix_from_args_failed_formatting():

    @error_prefix_from_args("error context {xx}")
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        ("error context {xx}\n"
         "...FAILED TO FORMAT args=(1,) kwargs={'y': 2}:"
         "\nan error"),
        f, 1, y=2
    )
