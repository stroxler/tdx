from __future__ import print_function
import functools

from ..wrapping import wraps, get_argspec


def assert_equal(x, y, msg=None):
    if msg is None:
        assert x == y
    else:
        assert x == y, msg


def test_get_argspec():

    msg = "Works when there's no __argspec__ attribute"

    def f(x): pass
    expected = ['x']
    actual = get_argspec(f).args
    assert_equal(actual, expected, msg)

    msg = "Works when there is an __argspec__ attribute"

    def f(x): pass
    f.__argspec__ = 'argspec'
    expected = 'argspec'
    actual = get_argspec(f)
    assert_equal(actual, expected, msg)


def test_wraps():
    """
    Test the wraps annotation. This indirectly tests the
    update_wrapper function, so we can omit unit tests of the latter.
    """

    def functools_decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            return 'wrapped'
        return wrapper

    def wrapping_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return 'wrapped'
        return wrapper

    @functools_decorator
    def f_lost_args(x, y): pass

    @wrapping_decorator
    def f_kept_args_one_level(x, y): pass

    @wrapping_decorator
    @wrapping_decorator
    def f_kept_args_two_levels(x, y): pass

    # make sure all of the functions actually got wrapped
    # (they would return None if they weren't wrapped)
    assert f_lost_args(0, 0) == 'wrapped'
    assert f_kept_args_one_level(0, 0) == 'wrapped'
    assert f_kept_args_two_levels(0, 0) == 'wrapped'

    good_args = ['x', 'y']
    bad_args = []

    # using a functools-built decorator should lose arg info
    actual = get_argspec(f_lost_args).args
    assert actual == bad_args

    # using a wrapping-built decorator should not lose arg info
    actual = get_argspec(f_kept_args_one_level).args
    assert actual == good_args

    # ...even if the annotations are stacked
    actual = get_argspec(f_kept_args_two_levels).args
    assert actual == good_args
