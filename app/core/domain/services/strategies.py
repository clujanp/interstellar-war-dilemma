from app.core.interfaces.repositories.strategies import StrategyRepository
from app.core.domain.models import Civilization, Planet
from app.core.interfaces.proxies import Proxy
from app.infraestructure.logging import logger
from app.config.messages import ERR_STRATEGY_SERVICE
from .memories import MemoriesServiceWrapper


class StrategyService:
    SHOW_TRACEBACK_VALIDATION: bool = False

    def __init__(
        self, repository: StrategyRepository, proxy_factory: callable
    ):
        self.repository = repository
        self.proxy_factory = proxy_factory

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

        def wrapper(
            self: Civilization,
            planet: Planet,
            opponent: Civilization,
        ) -> bool:
            opponent, planet, memories = mask(opponent, planet, self.memory)
            return strategy(
                opponent=opponent,
                planet=planet,
                memories=memories,
                resources=self.resources,
            )

        wrapper.name = strategy.__name__
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
            response = strategy(
                self=test_self,
                planet=test_planet,
                opponent=test_opponent,
            )
            if response not in [True, False]:
                raise ValueError(
                    ERR_STRATEGY_SERVICE['must_return'].format(
                        strategy.name, response))
            return True
        # TODO: improve error notification eg: share lineno
        except TypeError as err:
            logger.error(err, exc_info=self.SHOW_TRACEBACK_VALIDATION)
            return False
        except ValueError as err:
            logger.error(err, exc_info=self.SHOW_TRACEBACK_VALIDATION)
            return False
        except Exception as err:
            logger.error(err, exc_info=self.SHOW_TRACEBACK_VALIDATION)
            return False
        finally:
            # TODO: add to unit tests
            del test_planet
            del test_self
            del test_opponent
