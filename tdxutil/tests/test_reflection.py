from ..reflection import get_signature, get_call_arguments


# Small test of get_signature, mainly to document expected behavior -------

def test_get_signature():

    def f(): pass
    msg = "get_signature should handle functions with no arguments"
    expected = ([], None, None, [])
    actual = get_signature(f)
    print actual, expected
    assert actual == expected, msg

    def f(x, y): pass
    msg = "get_signature should handle functions with positional arguments"
    expected = (['x', 'y'], None, None, [])
    actual = get_signature(f)
    assert actual == expected, msg

    def f(*fargs): pass
    msg = "get_signature should handle functions with *vararg arguments"
    expected = ([], 'fargs', None, [])
    actual = get_signature(f)
    assert actual == expected, msg

    def f(**fkwargs): pass
    msg = "get_signature should handle functions with *kwarg arguments"
    expected = ([], None, 'fkwargs', [])
    actual = get_signature(f)
    assert actual == expected, msg

    def f(x, y=2, z=3): pass
    msg = "get_signature should handle functions with defaulted arguments"
    expected = (['x', 'y', 'z'], None, None, [2, 3])
    actual = get_signature(f)
    assert actual == expected, msg


# Test suite for get_call_arguments ------------------------------------------

def test_get_call_arguments_empty_call():
    def f(): pass
    args = []
    kwargs = {}
    expected = {}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_all_positional():
    def f(x, y): pass
    args = [1, 2]
    kwargs = {}
    expected = {'x': 1, 'y': 2}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_all_kwargs():
    def f(x, y): pass
    args = []
    kwargs = {'x': 1, 'y': 2}
    expected = {'x': 1, 'y': 2}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_missing_args():
    def f(x, y, z): pass
    args = [1]
    kwargs = {'z': 3}
    expected = {'x': 1, 'y': '__missing_argument_y__', 'z': 3}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_empty_varargs():
    def f(x, *fargs): pass
    args = []
    kwargs = {}
    expected = {'x': '__missing_argument_x__', 'fargs': []}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_nonempty_varargs():
    def f(x, *fargs): pass
    args = [1, 2, 3]
    kwargs = {}
    expected = {'x': 1, 'fargs': [2, 3]}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_empty_vkwargs():
    def f(x, **fkwargs): pass
    args = [1]
    kwargs = {}
    expected = {'x': 1, 'fkwargs': {}}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_nonempty_vkwargs():
    def f(x, **fkwargs): pass
    args = [1]
    kwargs = {'y': 3, 'z': 4}
    expected = {'x': 1, 'fkwargs': kwargs}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_all_defaulted_args():
    def f(x=1, y=2): pass
    args = []
    kwargs = {}
    expected = {'x': 1, 'y': 2}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_some_defaulted_args_some_pos():
    def f(x=1, y=2): pass
    args = [4]
    kwargs = {}
    expected = {'x': 4, 'y': 2}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_some_defaulted_args_some_kwargs():
    def f(x=1, y=2): pass
    args = []
    kwargs = {'y': 4}
    expected = {'x': 1, 'y': 4}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_extra_pos_args():
    """
    If there are extra positional arguments, ignore them
    (if there is no vararg in the signature)
    """
    def f(x=1, y=2): pass
    args = [1, 2, 3]
    kwargs = {}
    expected = {'x': 1, 'y': 2}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_extra_kwargs():
    """
    If there are extra keyword arguments, ignore them
    (if there is no packed kwarg in the signature)
    """
    def f(x=1, y=2): pass
    args = []
    kwargs = {'x': 1, 'y': 2, 'z': 5}
    expected = {'x': 1, 'y': 2}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_kitchen_sink_novarargs_legal():
    """
    Try a call using positional, regular kwargs, and
    packed kwargs. The call is legal.
    """
    def f(x, y=2, z=3, w=6, **fkwargs): pass
    args = [1, 2]
    kwargs = {'w': 4, 'this': 'that'}
    expected = {'x': 1, 'y': 2, 'z': 3, 'w': 4, 'fkwargs': {'this': 'that'}}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected


def test_get_call_arguments_kitchen_sink_varargs_legal():
    """
    Try a call using positional args, and both packed varargs
    and packed kwargs. The call is legal.
    """
    def f(x, y=2, z=3, w=6, *fargs, **fkwargs): pass
    args = [1, 2, 1, 2, 3, 2]
    kwargs = {'this': 'that'}
    expected = {'x': 1, 'y': 2, 'z': 1, 'w': 2,
                'fargs': [3, 2], 'fkwargs': {'this': 'that'}}
    actual = get_call_arguments(f, args, kwargs)
    assert actual == expected
