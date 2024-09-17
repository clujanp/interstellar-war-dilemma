from typing import Callable, Union, Any
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG
from app.application.logging import logger
from .proxy import SecureProxy


class SafeExecuter:
    def __init__(self, proxy_factory: 'ProxyFactory'):  # noqa F821
        self._proxy_factory = proxy_factory

    def __call__(self, method: callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            args, kwargs = self._unproxy_args(args, kwargs)
            return_value = method(*args, **kwargs)
            return self._proxy_return(return_value)
        return wrapper

    def _unproxy_args(self, args: tuple, kwargs: dict) -> tuple:
        logger.debug(ERR_MSG['debug_unproxy'].format(args, kwargs))
        return tuple(
            self._unproxy_arg(arg) for arg in args
        ), {
            key: self._unproxy_arg(value)
            for key, value in kwargs.items()
        }

    def _unproxy_arg(self, arg: Any) -> Any:
        if isinstance(arg, SecureProxy):
            return arg._obj
        return arg

    def _proxy_return(self, return_value: Any) -> Union[SecureProxy, Any]:
        if isinstance(return_value, dict):
            return {
                key: self._proxy_return(value)
                for key, value in return_value.items()
            }
        if isinstance(return_value, list):
            return [
                self._proxy_return(value)
                for value in return_value
            ]
        if isinstance(return_value, tuple):
            return tuple(
                self._proxy_return(value)
                for value in return_value
            )
        logger.debug(ERR_MSG['debug_proxy'].format(return_value.__repr__()))
        return self._proxy_factory(return_value, pass_=True)
