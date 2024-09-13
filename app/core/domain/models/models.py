from typing import List, Tuple, Optional, Dict, Callable
from pydantic import Field
from collections import defaultdict
from app.utils.decorators import cached
from .base import Entity
from .value_objects import Score, Result
from .validations import (
    PlanetValidations, CivilizationValidations, SkirmishValidations,
    MemoriesValidations
)


class Planet(Entity, PlanetValidations):
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

    def __repr__(self):
        return f"Planet: {self.name}"


class Civilization(Entity, CivilizationValidations):
    name: str
    strategy: Callable
    resources: int
    memory: 'Memories' = Field(default_factory=lambda: Memories(owner=None))

    def __str__(self):
        return f"{self.name} has {self.resources} resources"

    def __repr__(self):
        return f"Civilization: {self.name}"


class Skirmish(Entity, SkirmishValidations):
    planet: Planet
    civilization_1: Civilization
    civilization_2: Civilization
    posture_1: Optional[bool] = None
    posture_2: Optional[bool] = None
    winner_: Optional[List[Civilization]] = None
    score_1: Optional[int] = None
    score_2: Optional[int] = None

    @property
    def civilizations(self) -> Tuple[Civilization, Civilization]:
        return self.civilization_1, self.civilization_2

    @property
    def combined_score(self) -> int:
        return (self.score_1 or 0) + (self.score_2 or 0)

    @property
    def result(
        self
    ) -> Result.COOPERATION | Result.CONQUEST | Result.AGGRESSION:
        if all([self.posture_1, self.posture_2]):
            return Result.COOPERATION
        if any([self.posture_1, self.posture_2]):
            return Result.CONQUEST
        return Result.AGGRESSION

    def behavior(self, civilization: Civilization) -> Tuple[bool, Score]:
        if civilization == self.civilization_1:
            return self.posture_1, self.score_1
        if civilization == self.civilization_2:
            return self.posture_2, self.score_2
        raise ValueError("Civilization not in the skirmish")

    def __str__(self):
        if self.winner_ is None:
            return f"Skirmish in '{self.planet.name}' is disputing"
        if self.winner_ == []:
            return f"Skirmish in '{self.planet.name}' is fail for both"
        winners = ', '.join([c.name for c in self.winner_])
        return f"Skirmish in '{self.planet.name}' with winner {winners}"


class Round(Entity):
    number: int
    skirmishes: List[Skirmish]

    def __str__(self):
        return f"Round #{self.number} with {len(self.skirmishes)} skirmishes"


class Memories(Entity, MemoriesValidations):
    owner: Optional[Civilization]
    memories_: List[Skirmish] = Field(default_factory=list)
    owner_data: Dict[
        str,
        Optional[Planet | Civilization | str | int | float | bool]
    ] = Field(default_factory=dict)

    def add(self, skirmish: Skirmish) -> None:
        self.memories_.append(skirmish)
        self.skirmishes_by_civilization.cache_clear()
        self.skirmishes_count_by_civilization.cache_clear()

    @property
    def civilizations(self) -> List[Civilization]:
        return list(set([
            civilization
            for skirmish in self.memories_
            for civilization in (
                skirmish.civilization_1, skirmish.civilization_2)
            if civilization != self.owner
        ]))

    @property
    def skirmishes(self) -> List[Skirmish]:
        return self.memories_

    @cached
    def skirmishes_by_civilization(
        self
    ) -> Dict[Civilization, List[Tuple[bool, Score]]]:
        civilizations = defaultdict(list)
        for skirmish in self.memories_:
            for civilization in (
                skirmish.civilization_1, skirmish.civilization_2
            ):
                if civilization == self.owner:
                    continue
                civilizations[civilization].append(
                    skirmish.behavior(civilization))
        return dict(civilizations)

    @cached
    def skirmishes_count_by_civilization(self) -> Dict[Civilization, int]:
        civilizations = defaultdict(int)
        for skirmish in self.memories_:
            for civilization in (
                skirmish.civilization_1, skirmish.civilization_2
            ):
                if civilization == self.owner:
                    continue
                civilizations[civilization] += 1
        return dict(civilizations)

    def __str__(self):
        owner = ""
        if self.owner is not None:
            owner = f"{self.owner.name}'s "
        return f"{owner}Memories of {len(self.memories_)} skirmishes"
