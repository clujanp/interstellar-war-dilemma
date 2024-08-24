from typing import List, Any
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG


class WritableProxy:
    def __init__(self, obj: object, writable_attrs: List[str]):
        self._obj = obj
        self._writable_attrs = writable_attrs

    def __setattr__(self, name: str, value: Any) -> None:
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
