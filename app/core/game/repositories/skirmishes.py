from collections import OrderedDict
from .interfaces import ISkirmishesRepo
from ..models import CivilizationRegistration, SkirmishRelated


class SkirmishesRepo(ISkirmishesRepo):
    """Concrete implementation of the ISkirmishesRepo interface."""

    def __init__(self):
        self.__skirmishes: OrderedDict[
            SkirmishRelated, list[SkirmishRelated]
        ] = OrderedDict()

    def record_skirmish(self, skirmish: SkirmishRelated) -> None:
        """Records a skirmish in the repository."""
        if not isinstance(skirmish, SkirmishRelated):
            raise TypeError("Expected a SkirmishRelated instance.")
        self.__skirmishes.setdefault(skirmish.owner, []).append(skirmish)

    def query_skirmishes(
        self,
        owner: CivilizationRegistration,
        opponent: str | None = None,
        last: int = 100,
    ) -> list[SkirmishRelated]:
        """Queries the skirmishes given filters."""
        skirmishes = self.__skirmishes.get(owner, [])
        if opponent:
            skirmishes = [s for s in skirmishes if s.opponent == opponent]
        return skirmishes[-last:]
