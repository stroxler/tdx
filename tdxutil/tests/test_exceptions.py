from ..exceptions import (
    try_with_lazy_context,
    try_with_context,
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
