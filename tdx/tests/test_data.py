import pytest
from ..data import (
    read_json, read_yaml, write_json, read_content, write_content,
    path_from, directory_of, load_python_object,
)


def test_test_write_and_read_data(tmpdir):
    original = {
        'x': [1, 2],
        'y': 'a string'
    }
    f = tmpdir.mkdir('tests').join('dump.json')
    path = str(f)

    write_json(original, path)
    out_from_json = read_json(path)
    assert out_from_json == original

    out_from_yaml = read_yaml(path)
    assert out_from_yaml == original

    # make sure we raise if trying to write an existing file
    with pytest.raises(ValueError):
        write_json(original, path)


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
