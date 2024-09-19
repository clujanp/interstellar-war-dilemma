from abc import ABC, abstractmethod


class StrategyRepository(ABC):
    @abstractmethod
    def load_strategies(self) -> dict[str, callable]: ...
    @abstractmethod
    def select_random_builtin(self) -> callable: ...
