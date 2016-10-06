import os
import json
import yaml


def read_yaml(path):
    """
    Return the contents of a yaml file.
    """
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def read_json(path):
    """
    Return the contents of a json file, assuming utf-8 encoding
    """
    with open(path, 'r') as f:
        return json.load(f, encoding='utf-8')


def write_json(content, path, compact=False):
    """
    Write `content` to a json file at `path` with utf-8 encoding
    The file must not currently exist.

    If `compact` is True, we write with no whitespace, otherwise we use json
    pretty printing, with indent of 2.

    """
    _raise_if_exists(path)
    with open(path, 'w') as f:
        if compact:
            json.dump(content, f, encoding='utf-8')
        else:
            json.dump(content, f, indent=2, encoding='utf-8')


def write_content(content, path):
    """
    Write string content to a file at `path`.
    The file must not currently exist.
    """
    _raise_if_exists(path)
    with open(path, 'w') as f:
        f.write(content)


def read_content(path):
    """
    Read the contents of a file, return as a string

    """
    with open(path, 'r') as f:
        return f.read()


def _raise_if_exists(path):
    if os.path.exists(path):
        raise ValueError(
            "tdxutil write functions may only be used for new files, file "
            "%s exists" % path
        )
