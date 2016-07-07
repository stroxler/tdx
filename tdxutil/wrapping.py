"""
Variations on functools.update_wrapper and functools.wrap which attempt to
preserve argument information.

If you use these variations to stack decorators, you'll be able to use the
argument-inspection tools in reflection.py.

However, if you are mixing your own decorators with third-party decorators you
will need to make sure that anything relying on having argspecs available is
called underneath the third-party decorators, because most such decorators will
clobber the argument metadata.
"""
import functools
import inspect


WRAPPER_ASSIGNMENTS = functools.WRAPPER_ASSIGNMENTS
WRAPPER_UPDATES = functools.WRAPPER_UPDATES


def update_wrapper(wrapper,
                   wrapped,
                   assigned=WRAPPER_ASSIGNMENTS,
                   updated=WRAPPER_UPDATES):
    """
    Like functools.update_wrapper, except it also sets the __argspec__
    field.

    We first attempt to look up the __argspec__ field in `wrapped`,
    which allows us to use update_wrapper repeatedly when working
    with stacked decorators.

    If we fail to find wrapped.__argspec__, we instead use
    the output of inspect.getargspec() applied to `wrapped`.

    """
    wrapper = functools.update_wrapper(wrapper, wrapped, assigned, updated)
    setattr(wrapper, '__argspec__', get_argspec(wrapped))
    return wrapper


def wraps(wrapped,
          assigned=WRAPPER_ASSIGNMENTS,
          updated=WRAPPER_UPDATES):
    """
    Like the decorator functools.wraps, except it also
    persists the __argspec__ field.
    """
    return functools.partial(update_wrapper, wrapped=wrapped,
                             assigned=assigned, updated=updated)


def get_argspec(f):
    if hasattr(f, '__argspec__'):
        return getattr(f, '__argspec__')
    else:
        return inspect.getargspec(f)
