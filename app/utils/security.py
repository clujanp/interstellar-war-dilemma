from typing import List
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG


class SecureProxy:
    def __init__(
        self,
        obj: object,
        readable_attrs: List[str],
        writable_attrs: List[str],
        accessible_methods: List[str]
    ):
        self._obj = obj
        self._readable_attrs = readable_attrs
        self._writable_attrs = writable_attrs
        self._accessible_methods = accessible_methods

    def __getattr__(self, name: str) -> any:
        if name in self._readable_attrs:
            attr = getattr(self._obj.__class__, name, None)
            if isinstance(attr, property):
                return attr.fget(self._obj)
            value = getattr(self._obj, name)
            if callable(value):
                raise AttributeError(ERR_MSG['not_acc_methd'].format(name))
            return value
        elif name in self._accessible_methods:
            return getattr(self._obj, name)
        else:
            raise AttributeError(ERR_MSG['acc_restric'].format(name))

    def __setattr__(self, name: str, value: any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        elif name in self._writable_attrs:
            attr = getattr(self._obj.__class__, name, None)
            if isinstance(attr, property):
                if attr.fset is None:
                    raise AttributeError(ERR_MSG['not_modify'].format(name))
                attr.fset(self._obj, value)
            else:
                actual = getattr(self._obj, name)
                if callable(actual):
                    raise AttributeError(
                        ERR_MSG['methd_not_modify'].format(name))
                setattr(self._obj, name, value)
        else:
            raise AttributeError(ERR_MSG['not_modify'].format(name))
