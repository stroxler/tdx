from __future__ import print_function
import inspect
import time
import random
import json

import pytest
from ..decorators import (
    error_prefix_from_args, debug, _wrapt_proxy_decorator,
    wraptify, retry, print_json
)


# test wraptify tools ---------------

def test_wrapt_proxy_decorator():
    def f(x):
        return 1

    def g(y):
        return 2

    out = _wrapt_proxy_decorator(g)(f)
    assert out(1) == 2
    actual_argspec = inspect.getargspec(out)
    expected_argspec = inspect.ArgSpec(
        args=['x'], varargs=None,
        keywords=None, defaults=None
    )
    assert actual_argspec == expected_argspec


def test_wraptify():
    def double_output(f):
        "Decorator to wrap a function in a doubling operation"
        def wrapped(*args, **kwargs):
            return 2 * f(*args, **kwargs)
        return wrapped

    def f(x, y):
        "my docs for f"
        return x + y

    wraptified_double_output = wraptify(double_output)
    nowrapt = double_output(f)
    assert nowrapt(1, 2) == 6
    assert nowrapt.__doc__ is None
    yeswrapt = wraptified_double_output(f)
    assert yeswrapt(1, 2) == 6
    assert yeswrapt.__doc__ == "my docs for f"


# test the debug decorator ---------------

class MockDebugger(object):
    def __init__(self):
        self.called = False

    def post_mortem(self, tb):
        self.called = True


def test_debug_debugger_not_called_if_no_error():

    mock_debugger = MockDebugger()

    @debug(use_debugger=mock_debugger)
    def f(): return 0

    assert f() == 0
    assert not mock_debugger.called


def test_debug_debugger_not_called_if_debug_False():

    mock_debugger = MockDebugger()

    @debug(False, use_debugger=mock_debugger)
    def f(): raise Exception('error')

    with pytest.raises(Exception):
        f()


def test_debug_debugger_called_if_debug_True_and_raises():

    mock_debugger = MockDebugger()

    @debug(use_debugger=mock_debugger)
    def f(): raise Exception('error')

    f()
    assert mock_debugger.called


# test the error prefix decorators ---------------

def assert_error_with_prefix(prefix, func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        raise AssertionError("No error raised")
    except Exception as e:
        if not e.args[0].startswith(prefix):
            print("expected prefix %r" % prefix)
            print("actual message %r" % e.args[0])
            raise


def test_error_prefix_from_args_no_formatting():

    @error_prefix_from_args("error context")
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context:\nan error",
        f, 1, 2,
    )


def test_error_prefix_from_args_simple_formatting():

    @error_prefix_from_args("error context {x} {y} {z}")
    def f(x, y, z):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context 1 2 3:\nan error",
        f, 1, 2, 3
    )


def test_error_prefix_from_args_formatting_with_defaults():

    @error_prefix_from_args("error context {x} {y} {z}")
    def f(x, y=2, z=2):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context 1 2 3:\nan error",
        f, 1, z=3
    )


def test_error_prefix_from_args_formatting_with_packed_args():

    @error_prefix_from_args("error context {fargs} {fkwargs}")
    def f(*fargs, **fkwargs):
        raise ValueError("an error")

    assert_error_with_prefix(
        "error context (1, 2) {'z': 3}:\nan error",
        f, 1, 2, z=3
    )


def test_error_prefix_from_args_failed_formatting():

    @error_prefix_from_args("error context {xx}")
    def f(x, y):
        raise ValueError("an error")

    assert_error_with_prefix(
        ("error context {xx}\n"
         "...FAILED TO FORMAT args=(1,) kwargs={'y': 2}:"
         "\nan error"),
        f, 1, y=2
    )


# test the retry decorator ---------------------------------------------------

class Failer(object):
    """
    Class to help with creating test cases of the retry decorator
    """

    def __init__(self,
                 times_to_fail, attempts,
                 exception_to_raise=ValueError,
                 msg='test error', exceptions=(ValueError,),
                 warn_f=None, warn=True, warn_msg='oops',
                 wait_time=0, wait_multiplier=1,
                 jitter=0,
                 no_wait_first_retry=True, ):
        self.n_fail = 0
        self.times_to_fail = times_to_fail
        self.exception_to_raise = exception_to_raise
        self.msg = msg

        @retry(attempts, exceptions,
               warn=warn, warn_f=warn_f, warn_msg=warn_msg,
               wait_time=wait_time, wait_multiplier=wait_multiplier,
               jitter=jitter,
               no_wait_first_retry=no_wait_first_retry)
        def f():
            if self.n_fail < self.times_to_fail:
                self.n_fail += 1
                raise self.exception_to_raise(self.msg)
            else:
                return 42

        self.f = f


class WarnLogger(object):
    """
    Class to help with testing the warning messages of the retry decorator
    """

    def __init__(self):
        self.messages = []

    def warn(self, msg):
        self.messages.append(msg)


def test_retry_is_noop_if_f_does_not_raise():
    failer = Failer(
        times_to_fail=0, attempts=1,
    )
    assert failer.f() == 42
    assert failer.n_fail == 0


def test_retry_is_noop_if_f_raises_wrong_error():
    failer = Failer(
        times_to_fail=1, attempts=11, exception_to_raise=TypeError,
    )
    with pytest.raises(TypeError):
        failer.f()
    assert failer.n_fail == 1


def test_retry_will_catch_limited_failures():
    failer = Failer(
        times_to_fail=2, attempts=3,
    )
    assert failer.f() == 42
    assert failer.n_fail == 2


def test_retry_gives_up_after_attempts():
    failer = Failer(
        times_to_fail=10, attempts=3,
    )
    with pytest.raises(ValueError):
        failer.f()
    assert failer.n_fail == 3


def test_retry_warns_appropriately():
    # test that warn=False works
    warn_logger = WarnLogger()
    failer = Failer(
        times_to_fail=1, attempts=3,
        warn=False, warn_f=warn_logger.warn,
        warn_msg="oops {f}, {exception!r}, {n_failure}, {next_wait_s}",
    )
    failer.f()
    assert failer.n_fail == 1
    assert warn_logger.messages == []
    # test that warn=True works
    warn_logger = WarnLogger()
    failer = Failer(
        times_to_fail=1, attempts=3,
        warn=True, warn_f=warn_logger.warn,
        warn_msg="oops {f}, {exception!r}, {n_failure}, {next_wait_s}",
    )
    failer.f()
    assert failer.n_fail == 1
    assert warn_logger.messages == ["oops f, ValueError('test error',), 1, 0"]


def test_retry_backoff_with_no_wait_first(monkeypatch):
    times = []

    def mysleep(time):
        times.append(time)
    monkeypatch.setattr(time, 'sleep', mysleep)
    failer = Failer(
        times_to_fail=3, attempts=4, wait_time=1, wait_multiplier=2,
        no_wait_first_retry=True,
    )
    failer.f()
    assert times == [0, 1, 2]


def test_retry_backoff_with_wait_first(monkeypatch):
    times = []

    def mysleep(time):
        times.append(time)
    monkeypatch.setattr(time, 'sleep', mysleep)
    failer = Failer(
        times_to_fail=3, attempts=4, wait_time=1, wait_multiplier=2,
        no_wait_first_retry=False,
    )
    failer.f()
    assert times == [1, 2, 4]


def test_retry_backoff_randomized(monkeypatch):
    times = []

    def mysleep(time):
        times.append(time)

    def myuniform(a, b):
        return 0.5 * a
    monkeypatch.setattr(time, 'sleep', mysleep)
    monkeypatch.setattr(random, 'uniform', myuniform)
    failer = Failer(
        times_to_fail=2, attempts=3, wait_time=1, wait_multiplier=2,
        jitter=0.5,
        no_wait_first_retry=False,
    )
    failer.f()
    assert times == [0.75, 1.5]


def test_cli_jsonify_noargs(capsys):
    @print_json()
    def f(key, value, **kwargs):
        d = {key: value}
        for k, v in kwargs.items():
            d[k] = v
        return d

    f('x', 5, y=6)
    out, err = capsys.readouterr()
    assert err == ''
    assert out.strip() == json.dumps({'x': 5, 'y': 6}, indent=2)

    @print_json()
    def f(xs):
        return xs
    f([1, 2, 3])
    out, err = capsys.readouterr()
    assert err == ''
    assert out.strip() == json.dumps([1, 2, 3], indent=2)


def test_cli_jsonify_with_key(capsys):
    @print_json('key')
    def f():
        return 15

    f()
    out, err = capsys.readouterr()
    assert err == ''
    assert out.strip() == json.dumps({'key': 15}, indent=2)


def test_cli_jsonfiy_with_convert(capsys):
    def convert(value):
        return {'key': value + 1}

    @print_json(converter=convert)
    def f():
        return 15

    f()
    out, err = capsys.readouterr()
    assert err == ''
    assert out.strip() == json.dumps({'key': 16}, indent=2)
