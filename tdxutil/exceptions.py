"""
Tools to make working with exceptions easier.
"""


def try_with_context(error_context, f, *args, **kwargs):
    """
    Non-lazy version of `try_with_lazy_context`. Everything
    is the same except `error_context` should be a string.
    """
    return try_with_lazy_context(lambda: error_context,
                                 f, *args, **kwargs)


def try_with_lazy_context(error_context, f, *args, **kwargs):
    """
    Call an arbitrary function with arbitrary args / kwargs, wrapping
    in an exception handler that attaches a prefix to the exception
    message and then raises (the original stack trace is preserved).

    The `error_context` argument should be a lambda taking no
    arguments and returning a message which gets prepended to
    any errors.
    """
    try:
        return f(*args, **kwargs)
    except Exception as e:
        msg = error_context()
        e.args = tuple(
            ["%s:\n%s" % (msg, e.args[0])] + [a for a in e.args[1:]]
        )
        raise
