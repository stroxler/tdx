"""
Tools to make working with exceptions easier.
"""

from .reflection import get_call_arguments
from .wrapping import wraps


def error_context(context_message):
    """
    Decorator for wrapping any function in a call to
    `try_with_lazy_context`, with a context message that will be formatted
    based on the arguments of the call.

    If there is a formatting failure, the raw context_message is used,
    with 'FAILED TO FORMAT' appended. The failure to format does not
    interfere with raising the original exception.

    This decorator cannot in general be used after other decorators,
    because it relies on inspect.getargspec and most decorators clobber
    the metadata used by inspect.

    """
    def decorator(f):

        def format_context_message(args, kwargs):
            arguments = get_call_arguments(f, args, kwargs)
            try:
                return context_message.format(**arguments)
            except:
                return context_message + ' FAILED TO FORMAT'

        @wraps(f)
        def wrapped(*args, **kwargs):
            def error_context():
                return format_context_message(args, kwargs)
            return try_with_lazy_context(error_context, f, *args, **kwargs)

        return wrapped

    return decorator


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
