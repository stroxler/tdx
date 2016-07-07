"""
Utilities to help with writing more declarative code using
python container types.

Note: these functions are intended to enable clean code by replacing
often-repeated idioms of imperative programming. They are deliberately
simple. Neither features nor optimality are important goals, and they do no
error checking.

"""


def add_dicts(*args):
    """
    Combine dicts. If there are duplicate keys, raise an error.
    """
    new = {}
    for arg in args:
        for key in arg:
            if key in new:
                raise ValueError("Duplicate key: %r" % key)
            new[key] = arg[key]
    return new


def add_lists(*args):
    """
    Append lists. This is trivial but it's here for symmetry with add_dicts
    """
    out = []
    for arg in args:
        out.extend(arg)
    return out


def add_sets(*args):
    """
    Add sets. The arguments need not be sets. Returns a set of unique
    values. If the arguments include unhashable types, raises a TypeError.
    """
    out = set()
    for arg in args:
        for thing in arg:
            out.add(thing)
    return out


def flatten(*args):
    """
    Flatten a list of iterables. Returns an iterable.
    """
    for arg in args:
        for item in arg:
            yield item
