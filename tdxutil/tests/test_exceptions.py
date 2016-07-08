from ..exceptions import (
    try_with_lazy_context,
    try_with_context,
    error_context,
)


def assert_error_with_prefix(prefix, func, *args, **kwargs):
    try:
        print args
        func(*args, **kwargs)
        raise AssertionError("No error raised")
    except Exception as e:
        print e.args
        assert e.args[0].startswith(prefix)


def test_try_with_lazy_context():
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context:\nan error",
        try_with_lazy_context,
        lambda: "error context",
        f, 1, 2,
    )


def test_try_with_context():
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context:\nan error",
        try_with_context,
        "error context",
        f, 1, 2,
    )


def test_with_context_no_formatting():

    @error_context("error context")
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context:\nan error",
        f, 1, 2,
    )


def test_with_context_simple_formatting():

    @error_context("error context {x} {y} {z}")
    def f(x, y, z):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context 1 2 3:\nan error",
        f, 1, 2, 3
    )


def test_with_context_formatting_with_defaults():

    @error_context("error context {x} {y} {z}")
    def f(x, y=2, z=2):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context 1 2 3:\nan error",
        f, 1, z=3
    )


def test_with_context_formatting_with_packed_args():

    @error_context("error context {fargs} {fkwargs}")
    def f(*fargs, **fkwargs):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context (1, 2) {'z': 3}:\nan error",
        f, 1, 2, z=3
    )
