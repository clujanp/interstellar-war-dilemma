from abc import ABC, abstractmethod
from typing import Any, List


class Proxy(ABC):
    @abstractmethod
    def __init__(
        self,
        obj: object,
        readable_attrs: List[str],
        writable_attrs: List[str],
        accessible_methods: List[str],
        method_wrapper: callable = None,
    ): ...
    @abstractmethod
    def __getattr__(self, name: str): ...
    @abstractmethod
    def __setattr__(self, name: str, value: Any): ...
