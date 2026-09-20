from collections import OrderedDict
from inspect import signature, Parameter
from typing import Callable
import requests
from pydantic import ValidationError
from ...domain.value_objects import Decision
from .interfaces import IStrategy
from ..dto import AstroBodyDTO, StrategyResponseDto
from ..typing import StrategyCallable, URIApp, URIHttp


class StrategyRemote(IStrategy):
    """Concrete implementation of a remote strategy."""

    TIMEOUT = 2  # Timeout for HTTP requests in seconds

    def __init__(self, callback_uri: URIHttp):
        self.callback_uri = callback_uri

    def __call__(
        self, /, opponent: str, astro: AstroBodyDTO, resources: float,
    ) -> Decision:
        try:
            response: requests.Response = requests.post(
                self.callback_uri,
                json={
                    "opponent": opponent,
                    "astro": astro.model_dump(mode="json"),
                    "resources": resources,
                },
                timeout=self.TIMEOUT,
            )
            response.raise_for_status()
            StrategyResponseDto.model_validate(res_json := response.json())
            return Decision[res_json.get("decision")]
        except (requests.HTTPError, requests.ConnectTimeout, ValidationError):
            return Decision.NONE


class StrategyLocal(IStrategy):
    """Concrete implementation of a local strategy."""
    __registered_strategies: dict[URIApp, StrategyCallable] = {}

    def __init__(self, callback_uri: URIApp):
        self.local_strategy = self.__registered_strategies[callback_uri]

    def __call__(
        self, /, opponent: str, astro: AstroBodyDTO, resources: float,
    ) -> Decision:
        try:
            desicion = self.local_strategy(
                opponent=opponent, astro=astro, resources=resources)
            if not isinstance(desicion, Decision):
                desicion = Decision.NONE
        except Exception:  # pylint: disable=broad-exception-caught
            desicion = Decision.NONE
        return desicion

    @classmethod
    def register(cls, func: StrategyCallable) -> Callable:
        """Register decorator for a local strategy with the given path."""
        cls._check_function(func)
        path = f"app://{func.__name__}"
        cls.__registered_strategies[path] = func
        return func

    @staticmethod
    def _check_function(func: StrategyCallable) -> None:
        """Check function signature matches the expected strategy signature."""
        # pylint: disable=import-outside-toplevel
        from app.core.game import AstroBody, StrategyDecision

        expected_params = OrderedDict(
            opponent=Parameter(
                name="opponent",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str,
            ),
            astro=Parameter(
                name="astro",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=AstroBody,
            ),
            resources=Parameter(
                name="resources",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=float,
            ),
        )
        if not callable(func):
            raise ValueError(f"Function '{func}' must be callable")

        sign = signature(func)
        if sign.parameters != expected_params:
            raise ValueError(
                f"Function {func.__name__} must have parameters "
                f"{expected_params}, and given {sign.parameters}"
            )
        if sign.return_annotation is not StrategyDecision:
            raise ValueError(
                f"Function {func.__name__} must have return annotation like "
                "`-> StrategyDecision`"
            )
