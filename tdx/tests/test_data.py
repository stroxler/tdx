import json
import datetime
import textwrap
import pytest
from ..data import (
    read_json, read_yaml, write_json, read_content, write_content,
    path_from, directory_of, load_python_object, DateTimeEncoder,
    literal_unicode, write_yaml, yaml_string, json_string,
)


def test_write_json_and_read_data(tmpdir):
    original = {
        'x': [1, 2],
        'y': 'a string'
    }
    f = tmpdir.mkdir('tests').join('dump.json')
    path = str(f)

    # test that if we write as json we can read as yaml or json
    write_json(original, path)
    out_from_json = read_json(path)
    assert out_from_json == original

    out_from_yaml = read_yaml(path)
    assert out_from_yaml == original

    # make sure we raise if trying to write an existing file
    with pytest.raises(ValueError):
        write_json(original, path)


def test_write_yaml_and_read_data(tmpdir):
    original = {
        'x': [1, 2],
        'y': 'a string'
    }
    f = tmpdir.mkdir('tests').join('dump.json')
    path = str(f)

    # test that if we write as yaml we can read as yaml
    write_yaml(original, path)
    out_from_yaml = read_yaml(path)
    assert out_from_yaml == original

    # make sure we raise if trying to write an existing file
    with pytest.raises(ValueError):
        write_yaml(original, path)


def test_write_and_read_content(tmpdir):
    original = """
    Here is some
    string content
    """
    f = tmpdir.mkdir('tests').join('dump.txt')
    path = str(f)

    write_content(original, path)
    out = read_content(path)
    assert out == original

    # make sure we raise if trying to write an existing file
    with pytest.raises(ValueError):
        write_content(original, path)


def test_directory_of():
    filename = '/dir/file.txt'
    actual = directory_of(filename)
    expected = '/dir'
    assert actual == expected


def test_path_from():
    # a simple one-entry path
    filename = '/this/file.txt'
    actual = path_from(filename, 'that')
    expected = '/this/that'
    assert actual == expected
    # a multi entry path
    actual = path_from(filename, 'that', 'another')
    expected = '/this/that/another'
    assert actual == expected
    # a path where there are slashes
    actual = path_from(filename, 'that/another')
    expected = '/this/that/another'
    assert actual == expected


def test_load_python_object():
    # test that it works
    actual = load_python_object('collections.Set', 'abstract Set class')
    from collections import Set
    assert Set == actual
    # test that we catch ImportError
    with pytest.raises(ValueError):
        load_python_object('module_does_not_exist__.thing', 'thing')
    # test that we catch AttributeError
    with pytest.raises(ValueError):
        load_python_object('os.does_not_exist__', 'thing')


def test_DateTimeEncoder():
    original = {
        'date': datetime.date(1999, 1, 1),
        'datetime': datetime.datetime(1999, 1, 1, 1, 1, 1),
        'not_a_date': 'aa',
    }
    round_tripped = json.loads(json.dumps(original, cls=DateTimeEncoder))
    expected = {
        'date': original['date'].isoformat(),
        'datetime': original['datetime'].isoformat(),
        'not_a_date': original['not_a_date'],
    }
    assert round_tripped == expected


def test_json_string():
    content = {
        'key0': datetime.datetime(1999, 1, 1, 1, 1, 1)
    }
    actual = json_string(content, compact=True)
    expected = '{"key0": "1999-01-01T01:01:01"}'
    assert actual == expected


def test_yaml_string():
    content = {
        'key0': 'value',
        'key1': ['a', 'b', 'c'],
        'key2': True,
        'key3': 42,
        'key4': literal_unicode('a longer\n  string\nwith newlines')
    }
    actual = yaml_string(content, compact=False)
    expected = textwrap.dedent(
        """
        key0: value
        key1:
        - a
        - b
        - c
        key2: true
        key3: 42
        key4: |-
          a longer
            string
          with newlines
        """
    ).strip() + '\n'
    assert actual == expected
