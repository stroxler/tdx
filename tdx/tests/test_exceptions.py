import pytest
from ..exceptions import (
    error_prefix,
    lazy_error_prefix,
)


def f(x, y):
    "Function that raises an error"
    raise ValueError("an error")


def test_lazy_error_prefix():
    prefix = 'my error context'
    with pytest.raises(ValueError) as excinfo:
        with lazy_error_prefix(lambda: prefix):
            f(1, 2)
    e = excinfo.value
    assert e.args[0].startswith(prefix)


def test_error_prefix():
    prefix = 'my error context'
    with pytest.raises(ValueError) as excinfo:
        with error_prefix(prefix):
            f(1, 2)
    e = excinfo.value
    assert e.args[0].startswith(prefix)
