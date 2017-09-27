from __future__ import print_function

import sys

import pytest
try:
    import fire
except ImportError:
    raise RuntimeError("You must install fire to run tdx tests")

from ..cli import fire_cli
from .test_decorators import MockDebugger


the_value = ''


def set_value(name="steven"):
    global the_value
    the_value = name


def throw_error():
    raise RuntimeError


def test_fire_cli_no_special_flags():
    f = fire_cli(set_value)
    # run without args
    sys.argv = ["set-value"]
    f()
    assert the_value == 'steven'
    sys.argv = ["set-value", "troxler"]
    f()
    assert the_value == 'troxler'


def test_fire_cli_help_flag(capsys):
    global the_value
    the_value = ''
    f = fire_cli(set_value)
    sys.argv = ["set-value", "--help"]
    with pytest.raises(fire.core.FireExit):
        f()
    assert the_value == ''
    _, err = capsys.readouterr()
    help_message = '\n'.join([
        'Usage:       set-value [NAME]',
        '             set-value [--name NAME]',
    ])
    assert help_message in err


def test_fire_cli_debug_flag():
    mock_debugger = MockDebugger()
    f = fire_cli(throw_error, use_debugger=mock_debugger)
    sys.argv = ["throw-error", "--debug"]
    # note that the mock debugger winds up swallowing the error,
    # so we don't need a with pytest.raises block here
    f()
    assert mock_debugger.called
