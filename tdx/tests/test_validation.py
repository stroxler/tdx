import pytest

from ..validation import check_keys, ANY


def test_check_keys_on_empty_dict():
    d = {}
    required = []
    check_keys(d, required)


def test_check_keys_fails_if_both_allowed_and_optional():
    d = {'x': 1}
    required = ['x']
    allowed = ['x']
    optional = []
    with pytest.raises(ValueError):
        check_keys(d, required, allowed=allowed, optional=optional)


def test_check_keys_fails_if_required_missing_from_allowed():
    d = {'x': 1}
    required = ['x']
    allowed = []
    with pytest.raises(ValueError):
        check_keys(d, required, allowed=allowed)


def test_check_keys_raises_if_missing_required_keys():
    d = {}
    required = ['x']
    with pytest.raises(ValueError):
        check_keys(d, required)


def test_check_keys_passes_required_only():
    d = {'x': 1}
    required = ['x']
    check_keys(d, required)


def test_check_keys_raises_if_unknown_keys_required_only():
    d = {'x': 1, 'y': 2}
    required = ['x']
    with pytest.raises(ValueError):
        check_keys(d, required)


def test_check_keys_passes_with_allowed():
    d = {'x': 1, 'y': 2}
    required = ['x']
    allowed = ['x', 'y']
    check_keys(d, required, allowed=allowed)


def test_check_keys_raises_if_unknown_keys_with_allowed():
    d = {'x': 1, 'y': 2, 'z': 3}
    required = ['x']
    allowed = ['x', 'y']
    with pytest.raises(ValueError):
        check_keys(d, required, allowed=allowed)


def test_check_keys_passes_with_optional():
    d = {'x': 1, 'y': 2}
    required = ['x']
    optional = ['y']
    check_keys(d, required, optional=optional)


def test_check_keys_raises_if_unknown_keys_with_optional():
    d = {'x': 1, 'y': 2, 'z': 3}
    required = ['x']
    optional = ['y']
    with pytest.raises(ValueError):
        check_keys(d, required, optional=optional)


def test_check_keys_passes_if_allowed_is_ANY():
    d = {'x': 1, 'y': 2, 'z': 3}
    required = ['x']
    allowed = ANY
    check_keys(d, required, allowed=allowed)
