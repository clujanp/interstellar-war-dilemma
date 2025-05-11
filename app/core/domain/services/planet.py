from random import choice
from app.core.domain.models import Planet, Cost
from app.utils.functions import planet_namer


class PlanetService:
    AVAILABLE_COSTS = [Cost.HIGH, Cost.MEDIUM, Cost.LOW]

    @classmethod
    def create(cls, name: str = None, cost: Cost = None) -> Planet:
        return Planet(
            name=name or planet_namer(),
            cost=cost or choice(cls.AVAILABLE_COSTS)
        )
