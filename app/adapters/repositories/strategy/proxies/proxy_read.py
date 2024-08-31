from typing import List, Any
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG
from .exceptions import RestrictedAccessError


class ReadableProxy:
    def __init__(self, obj: object, readable_attrs: List[str]):
        self._obj = obj
        self._readable_attrs = readable_attrs

    def __getattr__(self, name: str) -> Any:
        if name in self._readable_attrs:
            attr = getattr(self._obj, name, None)
            if isinstance(attr, property):
                return attr.fget(self._obj)
            value = getattr(self._obj, name)
            if callable(value):
                raise RestrictedAccessError(
                    ERR_MSG['not_acc_methd'].format(name))
            return value
        raise RestrictedAccessError(ERR_MSG['acc_restric'].format(name))
