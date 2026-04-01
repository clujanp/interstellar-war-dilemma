from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models import Match, Round, Skirmish


class MatchRepository(ABC):
    """Port for Match aggregate persistence."""

    @abstractmethod
    def save(self, match: Match) -> UUID:
        """Persist match. Assigns and returns the id."""

    @abstractmethod
    def get(self, match_id: UUID) -> Match:
        """Retrieve a match by its id."""


class RoundRepository(ABC):
    """Port for Round persistence, scoped by match."""

    @abstractmethod
    def save(self, round: Round) -> None:
        """Persist a resolved round associated to a match."""

    @abstractmethod
    def get(self, round_id: UUID) -> Round:
        """Retrieve a round by its id."""

    @abstractmethod
    def list_by_match(self, match_id: UUID) -> list[Round]:
        """Retrieve all rounds for a given match."""

    @abstractmethod
    def get_by_match(self, match_id: UUID, round_number: int) -> Round:
        """Retrieve a specific round by match id and round number."""

    @abstractmethod
    def list(self) -> list[Round]:
        """Return all rounds in chronological insertion order."""


class SkirmishQueryRepository(ABC):
    """Port for read-only skirmish queries (used by MemoriesService)."""

    @abstractmethod
    def get_by_player(
        self,
        owner_id: UUID,
        opponent_id: UUID | None = None,
        last_n: int | None = None,
    ) -> list[Skirmish]:
        """Retrieve skirmishes involving a player, optionally filtered by opponent and limited."""
