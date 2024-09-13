from os import environ


DEFAULT_LANGUAGE = "en"


if environ.get("lANGUAGE", DEFAULT_LANGUAGE) == "en":
    from .en import (  # noqa: F811
        ERR_SECURE_PROXY,
        ERR_STRATEGY_SERVICE,
        ERR_MODELS_VALIDATIONS,
        ERR_LOCAL_REPOSITORY_STRATEGY,
        ERR_SKIRMISH_SERVICE,
    )


if environ.get("lANGUAGE", DEFAULT_LANGUAGE) == "es":
    from .es import (  # noqa: F811
        ERR_SECURE_PROXY,
        ERR_STRATEGY_SERVICE,
        ERR_MODELS_VALIDATIONS,
        ERR_LOCAL_REPOSITORY_STRATEGY,
        ERR_SKIRMISH_SERVICE,
    )


__all__ = [
    'ERR_SECURE_PROXY',
    'ERR_STRATEGY_SERVICE',
    'ERR_MODELS_VALIDATIONS',
    'ERR_LOCAL_REPOSITORY_STRATEGY',
    'ERR_SKIRMISH_SERVICE',
]
