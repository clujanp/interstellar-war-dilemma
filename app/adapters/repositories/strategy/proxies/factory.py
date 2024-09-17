from typing import List, Dict, Type, Literal, Union, Any
from app.core.interfaces.proxies import ProxyFactory
from app.config.messages import ERR_SECURE_PROXY as ERR_MSG
from app.utils.decorators import cached
from app.application.logging import logger
from .executer import SafeExecuter
from .proxy import SecureProxy


class SecureProxyFactory(ProxyFactory):
    def __init__(
        self,
        proxy_dfinitions: Dict[Type[Any], Dict[
            Literal[
                'readable_attrs',
                'writable_attrs',
                'accessible_methods'
            ], List[str]]]
    ):
        self._proxy_def = proxy_dfinitions
        self._safe_executer = SafeExecuter(self)

    @cached
    def __call__(
        self, obj: object, pass_: bool = False
    ) -> Union['SecureProxy', object]:
        cls = obj.__class__
        if cls in self._proxy_def:
            logger.debug(ERR_MSG['debug_secure_proxy'].format(obj.__repr__()))
            return SecureProxy(
                obj,
                self._proxy_def[cls]['readable_attrs'],
                self._proxy_def[cls]['writable_attrs'],
                self._proxy_def[cls]['accessible_methods'],
                method_wrapper=self._safe_executer,
            )
        if pass_:
            return obj
        raise AttributeError(
            ERR_MSG['not_secure_proxy'].format(cls.__name__))
