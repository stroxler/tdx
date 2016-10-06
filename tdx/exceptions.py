"""
Tools to make working with exceptions easier.
"""
import contextlib


def error_prefix(msg_prefix):
    """
    Non-lazy version of `lazy_error_context`. The `msg_prefix` argument
    should be a string.
    """
    return lazy_error_prefix(lambda: msg_prefix)


@contextlib.contextmanager
def lazy_error_prefix(msg_prefix_f):
    """
    Create an error context manager that attaches a prefix to the exception
    message and then raises (the original stack trace is preserved).

    The `error_context` argument should be a callable taking no arguments and
    returning a message which gets prepended to any errors.
    """
    try:
        yield
    except Exception as e:
        msg_prefix = msg_prefix_f()
        if len(e.args) == 0:
            e.args = (msg_prefix, )
        else:
            e.args = tuple(
                ["%s:\n%s" % (msg_prefix, e.args[0])] + [a for a in e.args[1:]]
            )
        raise
