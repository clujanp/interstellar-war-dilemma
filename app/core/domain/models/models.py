from typing import List, Tuple, Optional, Dict, Callable
from pydantic import Field
from collections import defaultdict
from app.utils.decorators import cached
from .base import Entity, NameableEntity
from .value_objects import Score, Position, Result
from .validations import (
    PlanetValidations, CivilizationValidations, SkirmishValidations,
    MemoriesValidations
)


class Planet(NameableEntity, PlanetValidations):
    cost: int
    colonized: bool = False
    colonizer: Optional[List['Civilization']] = None

    @property
    def colonizer_name(self) -> str:
        return (
            ' and '.join([c.name for c in self.colonizer])
            if self.colonizer
            else '<nobody>'
        )

    def __str__(self):
        return f"{self.name} is colonized by '{self.colonizer_name}'"

    def __repr__(self):
        return f"<Planet: {self.name}>"


class Civilization(NameableEntity, CivilizationValidations):
    strategy: Callable
    resources: int
    memory: 'Memories' = Field(default_factory=lambda: Memories(owner=None))

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"<Civilization: {self.name}>"


class Skirmish(Entity, SkirmishValidations):
    planet: Planet
    civilization_1: Civilization
    civilization_2: Civilization
    posture_1: Optional[Position] = None
    posture_2: Optional[Position] = None
    winner_: Optional[List[Civilization]] = None
    score_1: Optional[Score] = None
    score_2: Optional[Score] = None
    result: Optional[Result] = None

    @property
    def civilizations(self) -> Tuple[Civilization, Civilization]:
        return self.civilization_1, self.civilization_2

    @property
    def combined_score(self) -> int:
        return (self.score_1 or 0) + (self.score_2 or 0)

    def _behavior(self, civilization: Civilization) -> Tuple[Position, Score]:
        if civilization == self.civilization_1:
            return self.posture_1, self.score_1
        return self.posture_2, self.score_2

    def __str__(self):
        if self.winner_ is None:
            return f"Skirmish in '{self.planet.name}' is disputing"
        if self.winner_ == []:
            return f"Skirmish in '{self.planet.name}' is fail for both"
        winners = ', '.join([c.name for c in self.winner_])
        return f"Skirmish in '{self.planet.name}' with winner {winners}"

    def __repr__(self):
        return (
            f"<Skirmish: between {self.civilization_1.name} "
            f"and {self.civilization_2.name} in {self.planet.name}>"
        )


class Round(Entity):
    number: int
    skirmishes: List[Skirmish]

    def __str__(self):
        return f"Round #{self.number} with {len(self.skirmishes)} skirmishes"

    def __repr__(self):
        return f"<Round: {self.number}>"


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
        return list(set(
            civilization
            for skirmish in self.memories_
            for civilization in (
                skirmish.civilization_1, skirmish.civilization_2)
            if civilization != self.owner
        ))

    @property
    def skirmishes(self) -> List[Skirmish]:
        return self.memories_

    @cached
    def skirmishes_by_civilization(
        self
    ) -> Dict[Civilization, List[Tuple[Position, Score]]]:
        civilizations = defaultdict(list)
        for skirmish in self.memories_:
            for civilization in (
                skirmish.civilization_1, skirmish.civilization_2
            ):
                if civilization == self.owner:
                    continue
                civilizations[civilization].append(
                    skirmish._behavior(civilization))
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

    def __repr__(self):
        return f"<Memories: {self.owner}>"
