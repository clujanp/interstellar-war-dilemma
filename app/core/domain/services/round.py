from typing import List, Tuple
from app.core.domain.models import Civilization, Skirmish, Round
from .memories import MemoriesServiceWrapper


class RoundService:
    @classmethod
    def create(cls, number: int, skirmishes: List[Skirmish]) -> Round:
        return Round(number=number, skirmishes=skirmishes)

    @classmethod
    def decide_opponents(
        cls, civilizations: List[Civilization], memory: MemoriesServiceWrapper
    ) -> List[Tuple[Civilization, Civilization]]:
        ...
