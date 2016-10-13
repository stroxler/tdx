"Utilities for handling files and data and loading"
import importlib
import os
import json
import yaml


def load_python_object(identifier, descr):
    """
    Load a python object that's available from the current session

    Parameters
    ----------
    identifier : str
        A full python object identifier including modules, for example
        'np.linalg.lstsq'.
    descr : str
        A description of the thing you are trying to load, used to give
        better error messages if the load fails.

    Returns
    -------
    obj : object
        The loaded python object, for example if you have numpy
        installed on your system and ask for `'np.linalg.lstsq'`, we would
        return the `lstsq` function.

    Notes
    -----
    The main use case here is to allow user-input configuration, for
    example frameworks that define an interface and load user implementations
    at runtime.

    Examples
    --------
    >>> load_python_object("numpy.ndarray", "numpy ndarray function")
    """
    split_name = identifier.split('.')
    module_name = '.'.join(split_name[:-1])
    object_name = split_name[-1]
    try:
        module = importlib.import_module(module_name)
        return getattr(module, object_name)
    except ImportError:
        raise ValueError('Could not load %s module %s' % (descr, module_name))
    except AttributeError:
        raise ValueError('Could not load %r %s' % (descr, identifier))


def directory_of(filename):
    """
    Get the directory of the file specified by `filename`.

    Typically used from python modules which have resources to load,
    e.g. `THIS_DIR = this_dir(__file__)`
    """
    return os.path.dirname(os.path.abspath(filename))


def path_from(filename, *relative_path):
    """
    Given a filename (usually the __file__ of a python module) and
    a relative path to a resource from that file, return the filename
    to the relative resource.

    Since this might be used for reading or writing, we don't check that
    the resource exists.
    """
    return os.path.join(directory_of(filename), *relative_path)


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
