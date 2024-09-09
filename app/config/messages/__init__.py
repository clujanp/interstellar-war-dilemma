from os import environ


DEFAULT_LANGUAGE = "en"


if environ.get("lANGUAGE", DEFAULT_LANGUAGE) == "en":
    from .en import (  # noqa: F811
        ERR_SECURE_PROXY,
        ERR_STRATEGY_SERVICE,
        ERR_MODELS_VALIDATIONS,
    )


if environ.get("lANGUAGE", DEFAULT_LANGUAGE) == "es":
    from .es import (  # noqa: F811
        ERR_SECURE_PROXY,
        ERR_STRATEGY_SERVICE,
        ERR_MODELS_VALIDATIONS,
    )


__all__ = [
    'ERR_SECURE_PROXY',
    'ERR_STRATEGY_SERVICE',
    'ERR_MODELS_VALIDATIONS',
]
