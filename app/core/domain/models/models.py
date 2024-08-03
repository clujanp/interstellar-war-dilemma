from typing import List, Tuple, Optional, Dict, Callable
from pydantic import Field
from collections import defaultdict
from app.utils.decorators import cached
from .base import BaseModel
from .value_objects import Score
from .validations import (
    PlanetValidations, CivilizationValidations, SkirmishValidations,
    MemoriesValidations
)


class Planet(BaseModel, PlanetValidations):
    name: str
    cost: int
    colonized: bool = False
    colonizer: Optional[List['Civilization']] = None

    @property
    def colonizer_name(self) -> str:
        if self.colonizer:
            return ' and '.join([
                c.name for c in self.colonizer])
        return '<nobody>'

    def __str__(self):
        return f"{self.name} is colonized by '{self.colonizer_name}'"


class Civilization(BaseModel, CivilizationValidations):
    name: str
    strategy: Callable
    resources: int
    memory: 'Memories' = Field(default_factory=lambda: Memories(owner=None))

    def __str__(self):
        return f"{self.name} has {self.resources} resources"


class Skirmish(BaseModel, SkirmishValidations):
    planet: Planet
    civilization_1: Civilization
    civilization_2: Civilization
    posture_1: Optional[bool] = None
    posture_2: Optional[bool] = None
    winner_: Optional[List[Civilization]] = None
    score_1: Optional[int] = None
    score_2: Optional[int] = None

    def behavior(self, civilization: Civilization) -> Tuple[bool, Score]:
        if civilization == self.civilization_1:
            return self.posture_1, self.score_1
        if civilization == self.civilization_2:
            return self.posture_2, self.score_2
        raise ValueError("Civilization not in the skirmish")

    def __str__(self):
        if self.winner_ is None:
            return f"Skirmish in '{self.planet.name}' is disputing"
        winners = ', '.join([c.name for c in self.winner_])
        return f"Skirmish in '{self.planet.name}' with winner {winners}"


class Memories(BaseModel, MemoriesValidations):
    owner: Optional[Civilization]
    memories_: List[Skirmish] = Field(default_factory=list)

    def add(self, skirmish: Skirmish) -> None:
        self.memories_.append(skirmish)
        self.skirmishes.cache_clear()

    @property
    def civilizations(self) -> List[Civilization]:
        return list(set([
            civilization
            for skirmish in self.memories_
            for civilization in (
                skirmish.civilization_1, skirmish.civilization_2)
            if civilization != self.owner
        ]))

    @cached
    def skirmishes(self) -> Dict[Civilization, List[Tuple[bool, Score]]]:
        civilizations = defaultdict(list)
        for skirmish in self.memories_:
            for civilization in skirmish._winner:
                if civilization == self.owner:
                    continue
                civilizations[civilization].append(
                    skirmish.behavior(civilization))
        return dict(civilizations)

    def __str__(self):
        owner = ""
        if self.owner is not None:
            owner = f"{self.owner.name}'s "
        return f"{owner}Memories of {len(self.memories_)} skirmishes"
