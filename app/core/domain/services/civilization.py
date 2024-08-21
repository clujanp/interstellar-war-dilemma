from typing import Callable
from app.core.domain.models import Score, Civilization
from app.infraestructure.logging import logger
from .planet import PlanetService
from .memories import MemoriesServiceWrapper


class CivilizationService:
    @classmethod
    def create(
        cls,
        name: str,
        strategy: Callable,
        resources: int,
        skip_validation: bool = False
    ) -> Civilization:
        if not skip_validation:
            assert cls.validate_strategy(strategy), (
                f"Invalid strategy {name}")
        civilization = Civilization(
            name=name,
            strategy=strategy,
            resources=resources,
        )
        civilization.memory.owner = civilization
        civilization.memory = MemoriesServiceWrapper(civilization.memory)
        return civilization

    @classmethod
    def validate_strategy(cls, strategy: Callable) -> bool:
        test_planet = PlanetService.create(
            name="TestPlanet", cost=Score.COST_HIGH)
        test_self = cls.create(
            name="Self", strategy=lambda: True, resources=0,
            skip_validation=True
        )
        test_opponent = cls.create(
            name="TestOpponent", strategy=lambda: True, resources=0,
            skip_validation=True
        )
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
