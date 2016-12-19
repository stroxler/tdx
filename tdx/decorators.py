from __future__ import print_function

import warnings
import time
import random

import wrapt

from .inspectcall import get_callargs
from .exceptions import lazy_error_prefix


def wraptify(decorator):
    """
    By adding a wrapping layer, make a decorator handle metadata
    using wrapt

    PARAMETERS
    ----------
    decorator : callable
        A decorator which may not use wrapt for handling
        metadata (most libraries don't) and therefore may clobber
        some metadata

    RETURNS
    -------
    wraptified : callable
        A decorator whose output is the same as that of
        `decorator`, except with an extra layer of wrapping
        that takes no actions but attaches metadata based on
        the decorator target using wrapt

    This function is very useful when working with third-party
    decorators, most of which use functools.wraps and clobber
    the argspec. This will cause problems if, for example, you
    want the argspec to still be available in ipython or if you
    want to use functions like those from `tdx.inspectcall` that
    use the argspec.

    """
    def wraptified(wrapped):
        inner_wrapper = decorator(wrapped)
        outer_wrapper = _wrapt_proxy_decorator(inner_wrapper)(wrapped)
        return outer_wrapper

    return wraptified


def _wrapt_proxy_decorator(actual_wrapper):
    """
    Given a wrapper function which is the output of a call
    to some decorator (which does not use wrapt), return
    a new decorator which calls said wrapper (rather than the
    target of the decoration) but picks up metadata from the
    target function / object

    """
    @wrapt.decorator()
    def proxied_wrapper(nominal_target, instance, args, kwargs):
        return actual_wrapper(*args, **kwargs)
    return proxied_wrapper


def retry(attempts,
          exceptions=(Exception,),
          wait_time=1, wait_multiplier=2,
          jitter=0.1,
          no_wait_first_retry=True,
          warn=True, warn_f=None, warn_msg=None):
    """
    Decorate a function to retry on failures

    PARAMETERS
    ----------
    attemtps : int
        Total number of times to try (including the first)
    exceptions : tuple, optional
        A list or tuple of exception types to catch. If not specified then
        we catch Exception (so anything). Any exception that isn't a subtype
        of something in this tuple will be raised without retry.
    no_wait_first_retry : {True, False}, optional
        Should we start waiting wait_time seconds on the first retry? By
        default the very first retry is immediate, but you can toggle this
        behavior
    wait_time : {int, float}, optional
        Seconds to wait the first time we wait between retries (whether this
        happens before the first retry or the second depends on the value
        of `no_wait_first_retry`)
    wait_multiplier : {int, float}, optional
        Multiplier for wait time, to enable exponential backoff.
    jitter : {float}, optional
        jitter on the wait. The actual wait time between retries is
        (the actual wait time) +/- (a random uniform drawn from the
        interval [ - jitter * wait_time, + jitter * wait_time ])
          The purpose of randomization is to ensure that if failures are due to
        concurrency issues (for example you have several workers whose clients
        are trying to access a lockable resource at the same time) then
        separate processes don't retry in lock-step. If you set `jitter`
        to zero, you can disable it.
    warn : {True, False}, optional
        Should we warn on failures that are being retried?
    warn_f : callable, optional
        Function to call with warning message. If `None` and `warn` is True,
        then we use `warnings.warn`
    warn_msg : string, optional
        String to use in warning message. You can use the following
        format keys in your exception if you'd like:
            '{f}' for the name of the function
            '{exception}' for the exception caught
            '{n_failure}' for the number of failures so far
            '{next_wait_s}' for the time we'll wait till next retry

    RETURNS
    -------
    retry_wrapped : callable
        The original function wrapped in retry logic. The wrapping is done
        with wrapt so all the metadata should be preserved.

    """
    if not 0 <= jitter < 1:
        raise ValueError('`jitter` must be nonnegative and less than '
                         '1, got %r' % jitter)

    exceptions = tuple(exceptions)
    warn_f = warnings.warn if warn_f is None else warn_f
    warn_msg = ("Function {f} raised {exception!r}, retrying"
                if warn_msg is None else warn_msg)

    def randomized_wait(wait):
        return (1 + random.uniform(-jitter, jitter)) * wait

    @wrapt.decorator()
    def wrapper(f, instance, args, kwargs):
        wait = wait_time
        failed = 0
        while True:
            try:
                return f(*args, **kwargs)
            except exceptions as e:
                failed += 1
                if failed >= attempts:
                    raise
                if failed > 1 or (not no_wait_first_retry):
                    next_wait_s = randomized_wait(wait)
                    wait *= wait_multiplier
                else:
                    next_wait_s = 0
                if warn:
                    warn_f(warn_msg.format(
                        f=f.__name__, exception=e,
                        n_failure=failed,
                        next_wait_s=next_wait_s,
                    ))
                time.sleep(next_wait_s)

    return wrapper


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
    # ...traceback information, which is not affected...
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
    def wrapper(wrapped, instance, args, kwargs):

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

    return wrapper


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
    def wrapper(wrapped, instance, args, kwargs):
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

    return wrapper


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
