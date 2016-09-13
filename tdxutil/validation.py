"Utilities to help with common validation tasks"

ANY = True


def check_keys(d, required, allowed=None, optional=None, descr="the dictionary"):
    """
    Check that the keys of dictionary `d` are as expected. Raises an error when
    there are keys mismatches, which can be customized with the `descr` input.

    PARAMETERS
    ----------
    d : dict
       A dictionary to validate
    required : iterable
       An iterable of required keys. We raise an error if `d` is missing any
       of these.
    allowed : {iterable, ANY, None}
       Either `tdxutil.validation.ANY`, an iterable of allowed keys, or None. If
       `ANY`, then we only check required keys (i.e. unknown keys do not cause
       any errors). If an iterable, then we raise an error if `d` has any keys
       not here. If `None`, then the set of allowed keys will be inferred from
       `required` and `optional`
    optional : {iterable, None}, optional
       An iterable of optional keys. You may specify this as an alternative to 
       `allowed`, but you may not give non-`None` values for both of them. If
       both `allowed` and `optional` are `None`, then we will raise whenever
       `d`s keys do not match `required` exactly.
    descr : string, optional
       A description of the object being validated. Used in the error
       message.

    """
    if optional is not None and allowed is not None:
        raise ValueError("You may specify at most one of `allowed` and `optional`")
    # figure out what keys are permitted
    if allowed == ANY:
        pass
    elif allowed is not None:
        allowed = set(allowed)
        required_but_not_allowed = [r for r in required if r not in allowed]
        if len(required_but_not_allowed) > 0:
            raise ValueError()
    elif optional is not None:
        allowed = set.union(set(optional), set(required))
    else:
        allowed = set(required)
    # check for missing required keys
    keyset = set(d.keys())
    missing = [k for k in required if k not in keyset]
    # unless `allowed` is ANY, check for unexpected keys
    unexpected = [k for k in keyset if k not in allowed] if allowed != ANY else []
    if len(missing) > 0 or len(unexpected) > 0:
        raise ValueError(
            "Key mismatch in %s. Missing required keys %r, found unexpected keys %r" %
            (descr, missing, unexpected)
        )
