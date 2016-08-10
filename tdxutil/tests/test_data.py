import pytest
from ..data import (
    read_json, read_yaml, write_json, read_content, write_content
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
