import sys


def _patch_pydantic_typing_for_python_314_beta() -> None:
    """Work around pydantic 2.13.5 calling
    `typing._eval_type(..., prefer_fwd_module=True)` on Python 3.14, a kwarg
    dropped from CPython's `typing` module in this 3.14.0b3 build (the
    equivalent forward-module inference is now automatic). Without this, every
    `pydantic.BaseModel` subclass fails to resolve its annotations. Remove once
    pydantic ships an upstream fix for this CPython 3.14 pre-release.
    """
    if sys.version_info < (3, 14):
        return

    # pylint: disable=import-outside-toplevel
    import typing
    from pydantic._internal import _typing_extra

    def _eval_type(value, globalns=None, localns=None, type_params=None):
        try:
            # type: ignore[call-arg] # pylint: disable=unexpected-keyword-arg
            evaluated = typing._eval_type(  # pylint: disable=W0212
                value,
                globalns,
                localns,
                type_params=type_params,
                **{"prefer_fwd_module": True},
            )
        except TypeError:
            evaluated = typing._eval_type(  # pylint: disable=W0212
                value, globalns, localns, type_params=type_params)
        if evaluated is None:
            evaluated = type(None)
        return evaluated

    _typing_extra._eval_type = _eval_type  # pylint: disable=W0212


_patch_pydantic_typing_for_python_314_beta()
