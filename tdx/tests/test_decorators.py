import pytest
from ..decorators import (
    error_prefix_from_args, debug
)


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
