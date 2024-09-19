from typing import List, Callable
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG
from app.application.logging import logger
from app.utils.decorators import cached
from app.application.exceptions.proxy import RestrictedAccessError


class MethodAccessibleProxy:
    def __init__(
        self,
        obj: object,
        accessible_methods: List[str],
        method_wrapper: callable
    ):
        self._obj = obj
        self._accessible_methods = accessible_methods
        self._method_wrapper = method_wrapper

    @cached
    def __getattr__(self, name: str) -> Callable:
        if name in self._accessible_methods:
            if self._method_wrapper is None:
                return getattr(self._obj, name)
            logger.debug(ERR_MSG['debug_metd_warps'].format(
                name, self._obj.__repr__()))
            return self._method_wrapper(getattr(self._obj, name))
        else:
            raise RestrictedAccessError(ERR_MSG['acc_restric'].format(name))
