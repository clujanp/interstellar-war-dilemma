from collections import OrderedDict
from ...domain.models import AstroBody
from ..models import CivilizationRegistration, SkirmishRelated
from .interfaces import ISkirmishesRepo


class SkirmishesRepo(ISkirmishesRepo):
    """Concrete implementation of the ISkirmishesRepo interface."""

    def __init__(self):
        self.__skirmishes: OrderedDict[
            SkirmishRelated, list[SkirmishRelated]
        ] = OrderedDict()

    def record(self, skirmish: SkirmishRelated) -> None:
        """Records a skirmish in the repository."""
        if not isinstance(skirmish, SkirmishRelated):
            raise TypeError("Expected a SkirmishRelated instance.")
        self.__skirmishes.setdefault(skirmish.owner, []).append(skirmish)

    def list(self) -> list[SkirmishRelated]:
        """Lists all recorded skirmishes."""
        return [
            skirmish for skirmish_list in self.__skirmishes.values()
            for skirmish in skirmish_list
        ]

    def query(
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

    # TODO: make astros repository for better access of astro bodies
    def get_all_astro_bodies(self) -> set[AstroBody]:
        """Retrieves all astro bodies involved in skirmishes."""
        return set([
            sr.skirmish.astro_body
            for skirmish_list in self.__skirmishes.values()
            for sr in skirmish_list
        ])
