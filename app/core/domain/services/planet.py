from random import choice
from typing import Union
from app.core.domain.models import Planet, Cost
from app.utils.functions import planet_namer


class PlanetService:
    COSTS = [Cost.HIGH, Cost.MEDIUM, Cost.LOW]

    @classmethod
    def create(cls, name: str = None, cost: Union[*COSTS] = None) -> Planet:
        return Planet(
            name=name or planet_namer(),
            cost=cost or choice(cls.COSTS)
        )
