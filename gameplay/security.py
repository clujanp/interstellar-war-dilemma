from app.core.domain.models import Planet, Civilization
from typing import List, Callable
from contextlib import contextmanager


def secure_proxy(
    ro: List[str], rw: List[str] = None, methods: List[str] = None
) -> Callable:
    def decorator(cls: type) -> type:
        class SecureProxy(cls):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._ro = ro
                self._rw = rw or []
                self._methods = methods or []

            def __setattr__(self, name: str, value: any) -> None:
                if name in self._rw:
                    super().__setattr__(name, value)
                elif name in self._ro:
                    raise AttributeError(
                        f"Cannot modify read-only attribute: {name}")
                else:
                    super().__setattr__(name, value)

            def __getattribute__(self, name: str) -> any:
                if name in [
                    '_ro', '_rw', '_methods', '__class__', '__dict__',
                    '__module__', '__weakref__'
                ]:
                    return super().__getattribute__(name)
                if (
                    name in self._ro
                    or name in self._rw
                    or name in self._methods
                ):
                    attr = super().__getattribute__(name)
                    if callable(attr):
                        return self._method_wrapper(attr)
                    return attr
                raise AttributeError(
                    f"Access to attribute {name} is not allowed")

            def _method_wrapper(self, method: Callable) -> Callable:
                def wrapped_method(*args, **kwargs):
                    return method(*args, **kwargs)
                return wrapped_method

        return SecureProxy
    return decorator


@contextmanager
def secure_context(self: Civilization, planet: Planet, opponent: Civilization):
    SecurePlanet = secure_proxy(  # NOSONAR: S3341
        ro=['name', 'cost'],
        rw=['colonizer'],
        methods=['some_method']
    )(Planet)
    SecureCivilization = secure_proxy(  # NOSONAR: S3341
        ro=['name', 'resources'],
        rw=[],
        methods=['some_other_method']
    )(Civilization)

    secure_self = SecureCivilization(
        name=self.name,
        strategy=self.strategy,
        resources=self.resources
    )
    secure_planet = SecurePlanet(
        name=planet.name, cost=planet.cost, colonizer=planet.colonizer)
    secure_opponent = SecureCivilization(
        name=opponent.name,
        strategy=opponent.strategy,
        resources=opponent.resources
    )

    try:
        yield secure_self, secure_planet, secure_opponent
    finally:
        ...


def execute_strategy(
    strategy: Callable,
    self: Civilization,
    planet: Planet,
    opponent: Civilization,
) -> bool:
    with secure_context(
        self, planet, opponent
    ) as (secure_self, secure_planet, secure_opponent):
        return strategy(
            self=secure_planet, planet=secure_planet, opponent=secure_opponent)
