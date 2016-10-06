tdxutil: small tools for working with datatypes, data, and exceptions
---------------------------------------------------------------------

In `collections.py` there are some tools for working with lists,
sets, dicts, and iterables more declaratively.

In `data.py` there are some functiions to more concisely read and
write yaml in the most common use cases.

In `exceptions.py` there are some error handling tools. They are all
callback-oriented, so not necessarily user-friendly; mostly they are
intended for use in `decorators.py`.

In `decorators.py` there are some general decorator tools, in particular
one to wrap a function in a debugger call on error and one to attach
context to exception messages.
