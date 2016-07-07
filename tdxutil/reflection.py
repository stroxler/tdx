"Tools for using reflection to inspect function calls."
import inspect


def get_arguments(f, call_args, call_kwargs):
    """
    Given the signature of a function f, and the args and kwargs
    of a call to f, determine what the arguments of f were.

    Return them as a dict. The varargs of f (if any) will be a list
    and the kwargs of f (if any) will be a dict, each under the
    appropriate key.

    A note on error conditions: it's a bug if the returned arguments are ever
    completely incorrect, but in some edge cases where the arguments were
    misspecified (for example, an argument is given both positionally and
    as a keyword argument), the output becomes ambiguous. As a rule, if a
    TypeError would have been thrown by the call, then any ambiguously correct
    argument assignment is considered acceptable here.

    """
    spec = inspect.getargspec(f)
    arguments = {}
    if spec.varargs is not None:
        arguments[spec.varargs] = []
    if spec.keywords is not None:
        arguments[spec.keywords] = {}
    f_args = spec.args
    f_kwargs = spec.keywords
    f_varargs = spec.varargs
    f_defaults = spec.defaults

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
        return get_arguments_with_varargs(call_args, call_kwargs,
                                          f_args, f_varargs, f_kwargs)
    else:
        return get_arguments_no_varargs(call_args, call_kwargs,
                                        f_args, f_defaults, f_varargs,
                                        f_kwargs)


def get_arguments_with_varargs(call_args, call_kwargs,
                               f_args, f_varargs, f_kwargs):
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


def get_arguments_no_varargs(call_args, call_kwargs,
                             f_args, f_defaults, f_varargs, f_kwargs):
    arguments = {}
    # if varargs exist in the signature, add them as empty
    if f_varargs is not None:
        arguments[f_varargs] = []
    # handle all of the positional args in the call
    n_pos_arg = len(call_args)
    for name, value in zip(f_args, call_args):
        arguments[name] = value
    # handle all of the remaining regular args of f that have default
    # values, if any. This is easier to do by iterating backward
    for name, default in zip(f_args[n_pos_arg:][::-1], f_defaults[::-1]):
        if name in call_kwargs:
            arguments[name] = call_kwargs[name]
        else:
            arguments[name] = default
    # handle all of the remaining regular args of f that do not have
    # default values, if any. Either they are in kwargs or they are missing
    # (which would result in an exception, but since this code can
    # be used by exception-handling functions, we need to handle it)
    for name in f_args[n_pos_arg:-len(f_defaults)]:
        if name in call_kwargs:
            arguments[name] = call_kwargs[name]
        else:
            arguments[name] = '__missing_argument_{}__'.format(name)
    # set the f_kwargs key
    if f_kwargs is not None:
        arguments[f_kwargs] = {
            k: v for k, v in call_kwargs.iteritems() if k not in f_args
        }
    return arguments
