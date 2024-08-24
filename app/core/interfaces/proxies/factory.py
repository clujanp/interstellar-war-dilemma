from abc import ABC, abstractmethod


class ProxyFactory(ABC):
    @abstractmethod
    def __init__(self, proxy_dfinitions: dict[type, dict[str, list[str]]]): ...
    @abstractmethod
    def __call__(self, obj: object, pass_: bool = False): ...
