from random import choice
from typing import Union
from app.core.domain.models import Score, Planet
from app.utils.functions import planet_namer


class PlanetService:
    COSTS = [Score.COST_HIGH, Score.COST_MEDIUM, Score.COST_LOW]

    @classmethod
    def create(cls, name: str = None, cost: Union[*COSTS] = None) -> Planet:
        return Planet(
            name=name or planet_namer(),
            cost=cost or choice(cls.COSTS)
        )
