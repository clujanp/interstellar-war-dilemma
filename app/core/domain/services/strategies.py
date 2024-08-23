from app.core.interfaces.repositories.strategies import StrategyRepository
from app.core.domain.models import Civilization, Planet
from app.infraestructure.logging import logger


class StrategyService:
    def __init__(self, repository: StrategyRepository):
        self.repository = repository

    def load_strategies(self) -> dict[str, callable]:
        return self.repository.load_strategies()

    def mask_strategy(self, strategy: callable) -> callable:
        # TODO: mask for:
        # - new definition of stratgy args
        # - error handling
        # - cost pre validation and management
        return strategy

    def select_random_builtin(self) -> callable:
        return self.repository.select_random_builtin()

    @staticmethod
    def validate_strategy(
        strategy: callable,
        test_planet: Planet,
        test_self: Civilization,
        test_opponent: Civilization,
    ) -> bool:
        # TODO: adjust for improves in mask_strategy
        try:
            return strategy(
                self=test_self,
                planet=test_planet,
                opponent=test_opponent,
            ) in [True, False]
        # TODO: improve error notification eg: share lineno
        except TypeError as err:
            logger.error('-' * 80)
            logger.error(err, exc_info=True)
            logger.error('-' * 80)
            return False
        except Exception as err:
            logger.error('-' * 80)
            logger.error(err, exc_info=True)
            logger.error('-' * 80)
            return False
        finally:
            # TODO: add to unit tests
            del test_planet
            del test_self
            del test_opponent
