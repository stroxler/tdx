"Utilities for handling files and data and loading"
import importlib
import os
import json
import yaml
import datetime


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


def json_string(content, compact=False):
    """
    Write `content` as json

    """
    indent = (None if compact else 2)
    return json.dumps(content, indent=indent, encoding='utf-8',
                      cls=DateTimeEncoder)


def write_json(content, path, compact=False):
    """
    Write `content` to a json file at `path` with utf-8 encoding
    The file must not currently exist.

    If `compact` is True, we write with no whitespace, otherwise we use json
    pretty printing, with indent of 2.

    """
    _raise_if_exists(path)
    indent = (None if compact else 2)
    with open(path, 'w') as f:
        json.dump(content, f, indent=indent, encoding='utf-8',
                  cls=DateTimeEncoder)


def yaml_string(content, compact=False, _stream=None):
    """
    Write a python object to a yaml string.

    You can force literal strings by casting contents to `literal_unicode`

    """
    _init_yaml()
    return yaml.safe_dump(content, stream=_stream,
                          default_flow_style=compact)


def write_yaml(content, path, compact=False):
    """
    Write a python object to a yaml file. The file must not currently exist.

    You can force literal strings by casting contents to `literal_unicode`

    """
    _raise_if_exists(path)
    with open(path, 'w') as f:
        yaml_string(content, compact, _stream=f)


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


# utilities ------------------

class DateTimeEncoder(json.JSONEncoder):
    """
    Customized json encoder that can handle datetime.date and
    datetime.datetime; they are converted to iso format

    When you decode, the result will be a string (tdx does not currently have
    auto-decoding), but it should be easily machine-convertible

    Adapted from this Stack Overflow thread (extended to dates as well as datetimes)
    http://stackoverflow.com/questions/11875770/how-to-overcome-datetime-datetime-not-json-serializable-in-python # noqa
    """

    def default(self, o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def _raise_if_exists(path):
    if os.path.exists(path):
        raise ValueError(
            "tdxutil write functions may only be used for new files, file "
            "%s exists" % path
        )


class literal_unicode(unicode):
    """
    Class that lets users control when a yaml literal string
    (using the '|' character) will be used for output

    See http://stackoverflow.com/questions/6432605/any-yaml-libraries-in-python-that-support-dumping-of-long-strings-as-block-liter  # noqa
    """
    pass


_YAML_INITIALIZED = False


def _init_yaml():
    """
    Initialize yaml with customized tdx behavior
    """
    global _YAML_INITIALIZED
    if _YAML_INITIALIZED:
        return
    from yaml.representer import SafeRepresenter
    def change_style(style, representer):  # noqa
        def new_representer(dumper, data):
            scalar = representer(dumper, data)
            scalar.style = style
            return scalar
        return new_representer
    represent_literal_unicode = change_style(
        '|',
        SafeRepresenter.represent_unicode
    )
    yaml.SafeDumper.add_representer(
        literal_unicode, represent_literal_unicode
    )
