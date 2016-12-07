"""
Utilities to help with writing more declarative or concise
code using python container types.

Note: these functions are intended to enable clean code by replacing
often-repeated idioms of imperative programming. They are deliberately
simple. Neither features nor performance are important goals, and they do
little error checking.

"""
import re


class RaiseIfSpecifierNotFound(object):
    pass


def get_by_specifier(specifier, collection, default=RaiseIfSpecifierNotFound):
    """
    Given a collection (dict or list of dicts and lists -
    basically a json blob in python form), recursively find
    an entry using a specifier of the form
      "somekey.anotherkey[1].innerkey"

    For example, given the above string we would recursively
    look up
      `collection["somekey"]["anotherkey"][1]["innerkey"]

    This is likely to be particularly useful in command-line
    applications that need to grab data out of data structures
    based on bash input.

    If the specifier is invalid, we raise a ValueError. If the
    key lookup fails, we raise a ValueError if `default` is
    left at its default value of RaiseIfSpecifierNotFound, but
    otherwise we return the default.

    """
    keys = _specifier_to_keys(specifier)
    item = collection
    # TODO should we customize the message on lookup errors?
    try:
        for k in keys:
            item = item[k]
        return item
    except (IndexError, KeyError):
        if default is RaiseIfSpecifierNotFound:
            raise ValueError(
                'Failed to find key %r in specifier %r' %
                (k, specifier)
            )
        else:
            return default


def _specifier_to_keys(specifier):
    legal_specifier_rx = re.compile(r'(?:\w+|\[\d\])(?:\[\d+\]|\.\w+)*$')
    if not legal_specifier_rx.match(specifier):
        raise ValueError(
            "%r is not a legal specifier. Specifiers should "
            "look like, e.g., \"somekey[1].innerkey\"" %
            specifier
        )
    key_match_rx = re.compile(r'(\[([\d]+)\]|\w+)')
    keys = []
    for full_match, num_match in re.findall(key_match_rx, specifier):
        if num_match != '':
            keys.append(int(num_match))
        else:
            keys.append(full_match)
    return keys


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


def collect_by_key(pair_iter):
    """
    Collect an iterable of key, value pairs into a dict whose keys are the
    first entries in the pairs and whose values are lists of all the
    associated values, in the order they appeared.

    EXAMPLES
    >>> collect_by_key([(1, 2), (3, 4), (3, 5), (3, 5)])
    # {1: [2], 3: [4, 5, 5]}
    """
    out = {}
    for (k, v) in pair_iter:
        out[k] = out.get(k, [])
        out[k].append(v)
    return out
