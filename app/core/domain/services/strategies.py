from uuid import uuid4
from app.core.interfaces.repositories.strategies import StrategyRepository
from app.core.domain.models import Civilization, Planet, Position
from app.core.interfaces.proxies import Proxy
from app.infraestructure.exceptions.strategies import (
    NotSignedStrategyError, InvalidStrategyResponeError)
from app.infraestructure.logging import logger
from app.config.messages import ERR_STRATEGY_SERVICE as ERR_MSG
from .memories import MemoriesServiceWrapper


class StrategyService:
    SHOW_TRACEBACK_VALIDATION: bool = False

    def __init__(
        self, repository: StrategyRepository, proxy_factory: callable
    ):
        self.repository = repository
        self.proxy_factory = proxy_factory
        self.__signature = hash(uuid4())

    def load_strategies(self) -> dict[str, callable]:
        return self.repository.load_strategies()

    def mask_strategy(self, strategy: callable) -> callable:
        """
        for called with SkirmishService.resolve:
            strategy(
                self: Civilization,
                planet: Planet,
                opponent: Civilization,
            ) -> bool: COOPERATION | AGGRESSION
        for design:
            strategy(
                opponent: Civilization,
                planet: Planet,
                memories: MemoriesServiceWrapper,
                resources: int
            ) -> bool: COOPERATION | AGGRESSION
        """
        mask = self._mask_execution_entities
        SHOW_TRACEBACK_VALIDATION = self.SHOW_TRACEBACK_VALIDATION

        def wrapper(
            self: Civilization,
            planet: Planet,
            opponent: Civilization,
        ) -> bool:
            opponent, planet, memories = mask(opponent, planet, self.memory)
            try:
                position = strategy(
                    opponent=opponent,
                    planet=planet,
                    memories=memories,
                    resources=self.resources,
                )
                if position not in Position.VALID_RESPONSE:
                    raise InvalidStrategyResponeError(
                        ERR_MSG['must_return'].format
                        (strategy.__name__, position)
                    )
                return position
            except InvalidStrategyResponeError as err:
                logger.error(err, exc_info=SHOW_TRACEBACK_VALIDATION)
                return Position.FAIL
            except Exception as err:
                logger.error(err, exc_info=SHOW_TRACEBACK_VALIDATION)
                return Position.FAIL

        wrapper.name = strategy.__name__
        wrapper.__signature__ = self.__signature
        return wrapper

    def _mask_execution_entities(
        self,
        opponent: Civilization,
        planet: Planet,
        memories: MemoriesServiceWrapper,
    ) -> tuple[Proxy, Proxy, Proxy]:
        return (
            self.proxy_factory(opponent),
            self.proxy_factory(planet),
            self.proxy_factory(memories),
        )

    def select_random_builtin(self) -> callable:
        return self.repository.select_random_builtin()

    def validate_strategy(
        self,
        strategy: callable,
        test_planet: Planet,
        test_self: Civilization,
        test_opponent: Civilization,
    ) -> bool:
        try:
            if getattr(strategy, '__signature__', None) != self.__signature:
                raise NotSignedStrategyError(
                    ERR_MSG['signature'].format(strategy.name))
            response = strategy(
                self=test_self,
                planet=test_planet,
                opponent=test_opponent,
            )
            if response is Position.FAIL:
                return False
            return True
        except Exception as err:
            logger.critical(err, exc_info=self.SHOW_TRACEBACK_VALIDATION)
            return False
        finally:
            del test_planet
            del test_self
            del test_opponent
