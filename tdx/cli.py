import sys

from . import debug


def fire_cli(python_object, use_debugger=None):
    """
    Create a fire commandline interface with tweaked arg handling.

    PARAMETERS
    ----------
    python_object : {function, class}
        The python object to run as a fire command-line tool. You can
        run Fire with a python function for a simple command-line tool,
        or use an instance to get nested commands.
          Because we modify the command-line flag handling a bit, you
        cannot use `--help` or `--debug` to set `help` and `debug` kwargs
        on functions in this cli.
    use_debugger : debugger, optional
        See tdx.decorators.debug documentation

    RETURNS
    -------
    run_fire: function
        A function which, when called, runs fire.Fire.
        The flag handling is modified slightly so that the flags
        `--help` and `--debug` are reserved:
          * --debug will run the command under `tdx.debug` (which drops
            into a debugger on errors)
          * --help will run fire help, which in base fire requires
            `-- --help`

    NOTES
    -----
    Requires fire to be installed (which is *not* a tdx dependency)

    EXAMPLES
    --------
    A suggested pattern for using fire with nested commands is to use an
    instance of a dummy class. For instance, suppose you're in
    `mypackage/cli.py`, and you've defined `func_a` and `func_b` in
    `mypackage/core.py`. Then I could do this in `mypackage/cli.py` to define a
    command-line tool:
    ```
    from tdx.cli import use_fire
    from .core import func_a, func_b


    class FireSpec(object):

        def __init__(self):
            self.do_a = func_a
            self.do_b = func_b


    main = use_fire(FireSpec())
    ```
    and you'll get a command-line tool with subcommands `do-a` and `do-b`
    that run the functions. Note that we call it on an *instance* of
    `FireSpec`, not on the class itself; other patterns are possible, see
    the fire docs if you'd rather use a different pattern.

    If you want a more complex tool with nested subcommands, you can just
    extend the same pattern by making fields that are themselves instances of
    other `FireSpec`-type classes.

    """
    try:
        import fire
    except:
        raise ValueError("You must install fire to use tdx.fire_cli")

    def run_fire():
        fire.Fire(python_object)

    def run_cli():
        if '--help' in sys.argv:
            sys.argv = ([v for v in sys.argv if v != '--help'] +
                        ['--', '--help'])
        if '--debug' in sys.argv:
            sys.argv = [v for v in sys.argv if v != '--debug']
            debug(use_debugger=use_debugger)(run_fire)()
        else:
            run_fire()

    return run_cli
