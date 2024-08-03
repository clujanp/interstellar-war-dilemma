from typing import Callable
from app.core.domain.models import Score, Civilization, Skirmish
from app.infraestructure.logging import logger
from .planet import PlanetService


class CivilizationService:
    @classmethod
    def create(
        cls, name: str, strategy: Callable, resources: int
    ) -> Civilization:
        assert cls.validate_strategy(strategy), "Invalid strategy"
        civilization = Civilization(
            name=name,
            strategy=strategy,
            resources=resources,
        )
        civilization.memory.owner = civilization
        return civilization

    @staticmethod
    def validate_strategy(strategy: Callable) -> bool:
        test_planet = PlanetService.create(
            name="TestPlanet", cost=Score.COST_HIGH)
        test_opponent = Civilization(
            name="TestOpponent", strategy=lambda: True, resources=0)
        try:
            return strategy(
                planet=test_planet,
                opponent=test_opponent,
            ) in [True, False]
        except TypeError as err:
            logger.error(err)
            return False
        except Exception as err:
            logger.error(err, exc_info=True)
            return False

    @staticmethod
    def remember(civilization: Civilization, skirmish: Skirmish) -> None:
        civilization.memory.add(skirmish)
