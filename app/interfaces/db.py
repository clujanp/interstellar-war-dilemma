from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models import Match, Round, Skirmish


class MatchRepository(ABC):
    """Port for Match aggregate persistence."""

    @abstractmethod
    def save(self, match: Match) -> UUID:
        """Persist match. Assigns and returns the id."""

    @abstractmethod
    def get(self, match_id: UUID) -> Match: ...


class RoundRepository(ABC):
    """Port for Round persistence, scoped by match."""

    @abstractmethod
    def save(self, match_id: UUID, round: Round) -> None: ...

    @abstractmethod
    def get_by_match(self, match_id: UUID) -> list[Round]: ...

    @abstractmethod
    def get(self, match_id: UUID, round_number: int) -> Round: ...


class SkirmishQueryRepository(ABC):
    """Port for read-only skirmish queries (used by MemoriesService)."""

    @abstractmethod
    def get_by_player(
        self,
        owner_id: UUID,
        opponent_id: UUID | None = None,
        last_n: int | None = None,
    ) -> list[Skirmish]: ...
