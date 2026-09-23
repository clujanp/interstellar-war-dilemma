from collections import OrderedDict
from typing import Literal
from ..typing import URIAppHttps
from .interfaces import IStrategiesRepo, IStrategy
from .wrappers import StrategyRemote, StrategyLocal


class StrategiesRepo(IStrategiesRepo):
    """Concrete implementation of the strategies repository."""

    def __init__(self):
        self.__strategies: OrderedDict[
            tuple[URIAppHttps, str], IStrategy
        ] = OrderedDict()

    def register(
        self, callback_uri: URIAppHttps, name: str
    ) -> IStrategy:
        """Registers a strategy using the provided callback URI."""
        uri_type = self._classify_strategy_uri(callback_uri)
        self._check_registration(
            callback_uri, name, is_remote=uri_type == "remote")

        match uri_type:
            case "remote":
                strategy = StrategyRemote(callback_uri)
            case "local":
                strategy = StrategyLocal(callback_uri)

        self.__strategies[(callback_uri, name)] = strategy
        return strategy

    def unregister(
        self, callback_uri: URIAppHttps, name: str
    ) -> None:
        """Unregisters a strategy using the provided callback URI."""
        self.__strategies.pop((callback_uri, name), None)

    def get(
        self, callback_uri: URIAppHttps, name: str
    ) -> IStrategy | None:
        """Retrieves a strategy by its callback URI."""
        return self.__strategies.get((callback_uri, name))

    def list(self) -> list[IStrategy]:
        """Lists all registered strategies."""
        return list(self.__strategies.values())

    def _check_registration(
        self, callback_uri: URIAppHttps, name: str, is_remote: bool
    ) -> bool:
        """Checks if registered with given name
        and if the remote already in use."""
        if (callback_uri, name) in self.__strategies:
            return True
        if is_remote and (
            callback_uri in map(lambda key: key[0], self.__strategies)
        ):
            raise ValueError(
                f"A strategy with callback URI '{callback_uri}' "
                "is already registered under a different name."
            )
        return False

    @staticmethod
    def _classify_strategy_uri(uri: URIAppHttps) -> Literal['remote', 'local']:
        """Classifies the strategy URI as either 'local' or 'remote'."""
        if uri.startswith("http://") or uri.startswith("https://"):
            return "remote"
        if uri.startswith("app://"):
            return "local"
        raise ValueError(f"Unrecognized strategy URI scheme: '{uri}'")
