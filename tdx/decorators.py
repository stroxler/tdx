from __future__ import print_function

import wrapt

from .inspectcall import get_callargs
from .exceptions import lazy_error_prefix


def error_prefix_from_args(context_message):
    """
    Decorator for wrapping any function in a call to
    `tdxutil.exceptions.try_with_lazy_context`, with a context message that
    will be formatted based on the arguments of the call.

    PARAMETERS
    ----------
    context_message : str
        A message to prepend to any exceptions thrown by the function
        we are decorating. If an exception is thrown, we will format
        the context message with the arguments (including defaults)
        before raising.

    RETURNS
    -------
    decorator : function
        A decorator to wrap functions with error context prepending.
        If there's a problem formatting the message with the call
        arguments, the original message is prepended along with a
        message indicating a formatting error and the args / kwargs
        of the actual call.

    EXAMPLE
    -------

    >>> @error_context("In call, x={x}, y={y}, z={z}, fkwargs={fkwargs}")
    >>> def f(x, y=2, z=3, **fkwargs): raise Exception("error")

    >>> f(1, z=4, this='that')
    # ...traceback information, which isn't affected...
    # Exception: In call, x=1, y=2, z=4, fkwargs={'this': 'that'}:
    #    error

    NOTE
    ----
    This decorator depends on `inspect.getargspec` returning a
    correct argspec. This will work if you're using decorators that
    make use of the `wrapt` library, but `functools.wraps` will
    clobber some of the metadata needed. And many third-party decorators
    (for example, most click decorators) use `functools`, which means
    they destroy the information needed.

    To ensure that the argument information is still available when
    this decorator runs, you must ensure that all the decorators in
    between the raw function and this use `inspectcall.wrapping.wraps`.
    Generally I recommand making this the innermost decorator.

    """

    @wrapt.decorator
    def decorator(wrapped, instance, args, kwargs):

        def format_context_message():
            arguments = get_callargs(wrapped, *args, **kwargs)
            try:
                return context_message.format(**arguments)
            except:
                return (
                    context_message +
                    '\n...FAILED TO FORMAT args=%r kwargs=%r' % (args, kwargs)
                )

        with lazy_error_prefix(format_context_message):
            return wrapped(*args, **kwargs)

    return decorator


def debug(debug=True, delay=0, use_debugger=None):
    """
    Decorator to add debug-on-error to a function.

    PARAMETERS
    ----------
    debug : boolean, optional
        If false, the decorator just returns f. This allows you to
        decorate functions and toggle debugging on and off using
        global configuration.
    delay : {float, int}, optional
        We delay `delay` seconds prior to entering the debugger. By
        including this in function definitions, you give users some
        time to keyboard interrupt if, by reading the exception message,
        they already know what's wrong and don't want to debug.
    use_debugger : {module or object, None}, optional
        Allows the user to set a non-default debugger, such as the
        `ipdb` module. If unspecified, we will first try to use `pudb`
        and fall back to `pdb` if we don't find it.

    RETURNS
    -------
    decorator : function
        A decorator which wraps a function with logic to drop into
        a debugger if any exceptions are raised by the target function.

    """
    @wrapt.decorator
    def decorator(wrapped, instance, args, kwargs):
        try:
            return wrapped(*args, **kwargs)
        except:
            if not debug:
                raise
            import sys
            import traceback
            import time
            traceback.print_exc()
            print(("\nSleeping for %d seconds before debug, press C-c "
                   " to exit") % delay)
            time.sleep(delay)
            _, _, tb = sys.exc_info()
            if use_debugger is None:
                debugger = _get_debugger()
            else:
                debugger = use_debugger
            debugger.post_mortem(tb)

    return decorator


def _get_debugger():
    """
    Get a debugger for use in the debug wrapper. Factoring this out
    of the debug wrapper makes it a bit more pluggable, especially
    for tests.
    """
    try:
        import pudb
        return pudb
    except ImportError:
        print ("Using pudb not found, using pdb for post-mortem. "
               "Try pip install pudb.")
        import pdb
        return pdb
