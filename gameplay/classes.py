from typing import List, Optional
from ..strategy import BuiltInStrategies  # noqa: F401


# value objects
class Cost:
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    NONE = 0


class Position:
    COOPERATION = True
    AGGRESSION = False


class Score(int):
    LOSE = 0
    TIE_BAD = 1
    TIE_GOOD = 3
    WIN = 5


class Statistic(int):
    percent: float


# entities
class Planet:
    name: str
    cost: Cost.HIGH | Cost.MEDIUM | Cost.LOW | Cost.NONE


class Civilization:
    name: str


class Memories:
    length: int

    def civilizations(self) -> List[Civilization]: ...
    opponents = civilizations

    def skirmishes_count(self, civilization: Civilization) -> int: ...

    def last_position(
        self, civilization: Civilization
    ) -> Optional[Position.COOPERATION | Position.AGGRESSION]: ...

    def last_score(
        self, civilization: Civilization
    ) -> Optional[Score.WIN | Score.LOSE | Score.TIE_GOOD | Score.TIE_BAD]: ...

    def cooperations(self, civilization: Civilization) -> Statistic: ...
    def aggressions(self, civilization: Civilization) -> Statistic: ...
    def conquests(self, civilization: Civilization) -> Statistic: ...
    def hits(self, civilization: Civilization) -> Statistic: ...
    def loss(self, civilization: Civilization) -> Statistic: ...
    def mistakes(self, civilization: Civilization) -> Statistic: ...