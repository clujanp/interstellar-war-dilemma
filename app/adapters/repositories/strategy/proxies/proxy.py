from typing import List, Any
from app.core.interfaces.proxies import Proxy
from .proxy_read import ReadableProxy
from .proxy_write import WritableProxy
from .proxy_method import MethodAccessibleProxy


class SecureProxy(Proxy):
    def __init__(
        self,
        obj: object,
        readable_attrs: List[str],
        writable_attrs: List[str],
        accessible_methods: List[str],
        method_wrapper: callable = None,
    ):
        self._obj = obj
        self._readable_proxy = ReadableProxy(obj, readable_attrs)
        self._writable_proxy = WritableProxy(obj, writable_attrs)
        self._method_accessible_proxy = MethodAccessibleProxy(
            obj, accessible_methods, method_wrapper)

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._obj, name)
        if callable(value):
            return getattr(self._method_accessible_proxy, name)
        return getattr(self._readable_proxy, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            setattr(self._writable_proxy, name, value)
