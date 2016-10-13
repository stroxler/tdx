"Tools for using reflection to inspect function calls."
import inspect


def get_callargs(f, *call_args, **call_kwargs):
    """
    Return a dictionary mapping the names of arguments to f,
    including `*packed_varargs` and `**packed_kwargs` type arguments,
    to their values in the call to f.

    This function is intended to be usable for logging and exception
    handling, so it should never raise, which is part of what
    distinguishes it from the built-in `inspect.get_call_arguments`
    function.

    PARAMETERS
    ----------
    f : function or method
        Note that f cannot necessarily be an arbitrary callable, and
        also that many decorators will clobber the metadata needed. If
        you use `tdxutil.wrapping.wraps` for decorators, the metadata
        should still be available.
    call_args : tuple
        The positional arguments in a call to `f`.
    call_args : dict
        The keyword arguments in a call to `f`.

    RETURNS
    -------
    arguments: dict
        A dict whose keys are string names of arguments in the
        signature of f. All of the regular (non-packed) arguments
        are guaranteed to appear here; if they are missing in the call then
        they will be set to a value such as `"__missing_argument_x__"`. The
        packed varargs argument, if any exists in the signature of `f`, will be
        a possibly empty tuple. The packed kwargs argument, if any exists in
        the signature of `f`, will be a possibly empty dict.

    NOTES
    -----

    The python standard library has a very similar function,
    `inspect.getcallargs`. There are two reasons to use this implementation
    instead:
      * Because this implementation should never raise, it's more suitable
        for use in error-handling code (which is a common use case
        for decorators)
      * In speed tests, `get_call_arguments` seems to be very slightly
        faster, although for reasonably small argument lists both
        functions run in about 5-10 microseconds in tests on a
        2016 macbook pro.

    If there are extra positional or keyword arguments that make the call
    illegal, they will be ingored in the output. If a regular argument is
    specified both positionally and as a keyword argument, the positional
    specification wins in this function. Both of these situations would
    lead to a `TypeError` being raised if the call were actually attempted.

    In order for this method to work, the argspec of the function cannot
    be clobbered. If you are decorating a function with decorators that use
    `functools.wraps` to preserve metadata, the argspec metadata will be lost,
    but if you use `wrapt.decorator` then it will be preserved.

    EXAMPLES
    --------
    >>> def f(a, b, c, d=4, *stuff, **morestuff): pass

    >>> get_call_arguments(f, [1, 2], {'x':3})
    # {'a': 1,
    #  'b': 2,
    #  'c': '__missing_argument_c__',
    #  'd': 4,
    #  'morestuff': {'x': 3},
    #  'stuff': ()}

    >>> get_call_arguments(f, [1, 2, 3, 4, 5, 6], {'x':3})
    # {'a': 1,
    #  'b': 2,
    #  'c': 3,
    #  'd': 4,
    #  'morestuff': {'x': 3},
    #  'stuff': (5, 6)}

    See the tests for more examples.

    """
    f_argspec = inspect.getargspec(f)
    return callargs_from_argspec(f_argspec, *call_args, **call_kwargs)


def callargs_from_argspec(f_argspec, *call_args, **call_kwargs):
    """
    Like get_callargs (see that function for docs) except instead of
    passing in a callable f, we pass in its argspec.

    The reason this function exists is that sometimes we have to do
    an end-run around the usual argspec. For example, in the `clickutil`
    package I have been unable to make the metadata of a click-decorated
    function match that of the original function (wrapt doesn't work
    with click because the decorators are classes, not wrapper unctions,
    so I cannot just wraptify the click decorators). By separating
    out the core logic that depends only on the argspec, I make the
    `tdx` module more flexible and useful in more situations.

    """
    f_args, f_varargs, f_kwargs, f_defaults = get_signature(f_argspec)

    # there are two major cases which are easier to deal with
    # separately:
    #  * if the number of positional args in the call
    #    exceeds the number of regular args of f, then there are
    #    varargs, and also none of f's regular args are specified
    #    via kwargs in the call or default values
    #  * otherwise, there are no varargs, and we have to check
    #    kwargs of the call and default values for some of the
    #    regular arguments of f
    if len(call_args) > len(f_args):
        return _get_arguments_extra_positional(
            call_args, call_kwargs,
            f_args, f_varargs, f_kwargs
        )
    else:
        return _get_arguments_no_extra_positional(
            call_args, call_kwargs,
            f_args, f_defaults, f_varargs, f_kwargs
        )


def get_signature(argspec):
    """
    Return a tuple (args, defaults, varargs, kwargs) from a function
    signature. If there are no varargs, then `varargs` is None.

    PARAMETERS
    ----------
    f : function or method
        Note that f cannot necessarily be an arbitrary callable, and
        also that many decorators will clobber the metadata needed. If
        you use `tdxutil.wrapping.wraps` for decorators, the metadata
        should still be available.

    RETURNS
    -------
    args : list
        A list of the string names of all regular arguments (not unpacked
        varargs or keyword args) of `f`.
    varargs : {None, str}
        If the signature of f contains a varargs positional argument,
        this will be the string name of that argument. (For example if
        the argument list contains `*myvarargs` we get `"myvarargs"``).
        If there is no vararg argument, this will be None.
    kwargs : {None, str}
        If the signature of f contains a packed keyword argument,
        this will be the string name of that argument. (For example if
        the argument list contains `**mykwargs` we get `"mykwargs"``).
        If there is no packed keyword argument, this will be None.
    defaults : list
        A list of all the default values for regular arguments of `f`.
        In general it can be shorter than `args`, and `defaults` will
        be aligned with `args[-len(defaults):]`

    EXAMPLES
    --------
    >>> def f(a, b=3, c=5, *stuff, **morestuff): pass

    >>> get_signature(f)
    # (['a', 'b', 'c'], [3, 5], 'stuff', 'morestuff')

    >>> def f(x, y): pass

    >>> get_signature(f)
    # (['x', 'y'], [], None, None)
    """
    f_args = argspec.args
    f_varargs = argspec.varargs
    f_kwargs = argspec.keywords
    f_defaults = [] if argspec.defaults is None else list(argspec.defaults)
    return f_args, f_varargs, f_kwargs, f_defaults


def _get_arguments_extra_positional(call_args, call_kwargs,
                                    f_args, f_varargs, f_kwargs,):
    arguments = {}
    # handle all of the regular args of f
    n_f_args = len(f_args)
    for name, value in zip(f_args, call_args):
        arguments[name] = value
    # set the f_varargs key
    # -------------------
    # we need the check on f_varargs because if the user made an argument
    # mismatch error, then f may not have varargs.
    if f_varargs is not None:
        arguments[f_varargs] = call_args[n_f_args:]
    # set the f_kwargs key
    # --------------------
    # Again, we need a check because there can be param mismatches
    if f_kwargs is not None:
        arguments[f_kwargs] = call_kwargs
    return arguments


def _get_arguments_no_extra_positional(call_args, call_kwargs,
                                       f_args, f_defaults, f_varargs,
                                       f_kwargs):
    arguments = {}
    # if varargs exist in the signature, add them as empty
    if f_varargs is not None:
        arguments[f_varargs] = ()
    # segment the regular arguments of f into three groups
    #  * everything before end_positional is specified positionally
    #    in the call, regardless of whether it has a default value
    #  * everything between end_positional and start_defaulted must
    #    either be specified via a kwarg in the call or be missing
    #  * everything after start_defaulted has a default value and is
    #    not positional, so it either was a kwarg in the call or has the
    #    default value
    n_args = len(f_args)
    n_positional = len(call_args)
    n_no_defaults = n_args - len(f_defaults)
    for i, name in enumerate(f_args):
        # if there's a positional argument in the call, that's what we use
        if i < n_positional:
            arguments[name] = call_args[i]
        else:
            # if there's no positional arg but there is a kwarg in the call,
            # that's what we use
            if name in call_kwargs:
                arguments[name] = call_kwargs[name]
            else:
                # otherwise either we use a default from the signature of
                # f or the argument is missing.
                idx_in_defaults = i - n_no_defaults
                if idx_in_defaults >= 0:
                    arguments[name] = f_defaults[idx_in_defaults]
                else:
                    arguments[name] = '__missing_argument_{}__'.format(name)
    # set the f_kwargs key
    if f_kwargs is not None:
        arguments[f_kwargs] = {
            k: v for k, v in call_kwargs.iteritems() if k not in f_args
        }
    return arguments
