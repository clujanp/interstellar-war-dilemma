from typing import List, Callable, Tuple
from app.core.domain.services import (
    PlanetService, StrategyService, CivilizationService, SkirmishService,
    RoundService, MemoriesServiceWrapper
)
from app.core.domain.models import Planet, Civilization, Skirmish, Round, Cost


class PlanetUseCases:
    def __init__(self, service: PlanetService):
        self.service = service

    def generate(self, quantity: int) -> List[Planet]:
        return [self.service.create() for _ in range(quantity)]


class StrategiesUseCases:
    def __init__(
        self,
        service: StrategyService,
        planet_service: PlanetService,
        civilization_service: CivilizationService,
    ):
        self.service = service
        self.planet_service = planet_service
        self.civilization_service = civilization_service

    def load_strategies(self) -> dict[str, callable]:
        strategies = self.service.load_strategies()
        test_planet, test_self, test_opponent = self._get_test_entities()
        valid_strategies = {}
        for name, strategy in strategies.items():
            strategy = self.service.mask_strategy(strategy)
            if self.service.validate_strategy(
                strategy, test_planet, test_self, test_opponent
            ):
                valid_strategies[name] = strategy
        return valid_strategies

    def _get_test_entities(self) -> Tuple[Planet, Civilization, Civilization]:
        return (
            self.planet_service.create(name="TestPlanet", cost=Cost.HIGH),
            self.civilization_service.create(
                name="Self", strategy=lambda: True, resources=0),
            self.civilization_service.create(
                name="TestOpponent", strategy=lambda: True, resources=0),
        )

    def select_random_builtin(self) -> callable:
        return self.service.select_random_builtin()


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
        return RoundService.decide_opponents(civilizations)

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
