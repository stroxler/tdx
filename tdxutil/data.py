import os
import json
import yaml


def read_yaml(path):
    """
    Return the contents of a yaml file
    """
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def read_json(path):
    """
    Return the contents of a json file
    """
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def write_json(content, path, compact=False):
    """
    Write `content` to a json file at `path`.
    The file must not currently exist.

    If `compact` is True, we write with no whitespace, otherwise we use json
    pretty printing, with indent of 2.

    """
    if os.path.exists(path):
        raise ValueError(
            "write_json may only be used for new files, file "
            "%s exists" % path
        )
    with open(path, 'w') as f:
        if compact:
            json.dump(content, f)
        else:
            json.dump(content, f, indent=2)
