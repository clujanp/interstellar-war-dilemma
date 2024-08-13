from random import choices
from typing import List, Callable, Tuple
from app.core.domain.services import (
    PlanetService, CivilizationService, SkirmishService, RoundService,
    MemoriesServiceWrapper
)
from app.core.domain.models import Planet, Civilization, Skirmish, Round
from app.infraestructure.logging import logger


class PlanetUseCases:
    def __init__(self, service: PlanetService):
        self.service = service

    def generate(self, quantity: int) -> List[Planet]:
        return [self.service.create() for _ in range(quantity)]


class CivilizationUseCases:
    def __init__(self, service: CivilizationService):
        self.service = service

    def register(
        self, name: str, strategy: Callable, resources: int
    ) -> Civilization:
        return self.service.create(name, strategy, resources)


class SkirmishUseCases:
    def __init__(self, service: SkirmishService):
        self.service = service

    def create(
        self,
        opponents: List[Tuple[Civilization, Civilization]],
        planets: List[Planet],
    ) -> List[Skirmish]:
        assert len(opponents) == len(planets), "Invalid number of skirmishes"
        skirmishes: List[Skirmish] = []
        for _opponents, planet in zip(opponents, planets):
            opponent_1, opponent_2 = _opponents
            skirmish = self.service.create(planet, opponent_1, opponent_2)
            skirmishes.append(skirmish)
        return skirmishes

    def resolve(self, skirmishes: List[Skirmish]) -> None:
        for skirmish in skirmishes:
            self.service.resolve(skirmish)


class RoundUseCases:
    def __init__(self, service: RoundService):
        self.service = service

    @staticmethod
    def decide_opponents(
        civilizations: List[Civilization]
    ) -> List[Tuple[Civilization, Civilization]]:
        assert len(civilizations) % 2 == 0, "Invalid number of civilizations"

        done = []
        opponents = []
        for civilization in civilizations:
            if civilization not in done:
                odds = {
                    opponent: (
                        (civilization.memory.length + 1)
                        - civilization.memory.skirmishes_count(opponent)
                    )
                    for opponent in civilizations
                    if opponent != civilization and opponent not in done
                }
                options, weights = zip(*odds.items())
                opponent = choices(options, weights=weights, k=1)[0]
                opponents.append((civilization, opponent,))
                done.append(civilization)
                done.append(opponent)
        return opponents

    def create_round(self, number: int, skirmishes: List[Skirmish]) -> Round:
        return self.service.create(number, skirmishes)


class MemoriesUseCases:
    def __init__(self):
        self.service = MemoriesServiceWrapper()

    def record_round_in_memories(
        self, skirmishes: List[Skirmish]
    ) -> None:
        for skirmish in skirmishes:
            for civilization in skirmish.civilizations:
                civilization.memory.remember(skirmish)
            self.service.remember(skirmish)

    def summary(self) -> str:
        return self.service.summary()

    def report(self) -> str:
        return self.service.report()

    def save(self) -> None:
        self.service.save()
