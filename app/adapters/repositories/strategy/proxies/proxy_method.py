from typing import List, Callable
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG
from app.infraestructure.logging import logger
from .exceptions import RestrictedAccessError


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

    def __getattr__(self, name: str) -> Callable:
        if name in self._accessible_methods:
            if self._method_wrapper is None:
                return getattr(self._obj, name)
            return self._method_wrapper(getattr(self._obj, name))
        else:
            raise RestrictedAccessError(ERR_MSG['acc_restric'].format(name))
