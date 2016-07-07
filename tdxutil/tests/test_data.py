from ..data import read_json, read_yaml, write_json


def test_write_and_load(tmpdir):
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
