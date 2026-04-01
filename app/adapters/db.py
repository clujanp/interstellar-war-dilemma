from uuid import UUID

from app.domain.models import Match, Round, Skirmish
from app.interfaces.db import (
    MatchRepository,
    RoundRepository,
    SkirmishQueryRepository,
)


class InMemoryMatchRepository(MatchRepository):
    """In-memory adapter for Match persistence."""

    def __init__(self) -> None:
        self._store: dict[UUID, Match] = {}

    def save(self, match: Match) -> UUID:
        self._store[match.id] = match
        return match.id

    def get(self, match_id: UUID) -> Match:
        match = self._store.get(match_id)
        if match is None:
            raise KeyError(f"Match '{match_id}' not found.")
        return match


class InMemoryRoundRepository(RoundRepository):
    """In-memory adapter for Round persistence."""

    def __init__(self) -> None:
        self._store: list[Round] = []

    def save(self, round: Round) -> None:
        self._store.append(round)

    def get(self, round_id: UUID) -> Round:
        for r in self._store:
            if r.id == round_id:
                return r
        raise KeyError(f"Round '{round_id}' not found.")

    def list_by_match(self, match_id: UUID) -> list[Round]:
        return [r for r in self._store if r.match.id == match_id]

    def get_by_match(self, match_id: UUID, round_number: int) -> Round:
        for r in self._store:
            if r.match.id == match_id and r.number == round_number:
                return r
        raise KeyError(
            f"Round {round_number} not found for match '{match_id}'.")

    def list(self) -> list[Round]:
        """Return all rounds in insertion order."""
        return list(self._store)


class InMemorySkirmishQueryRepository(SkirmishQueryRepository):
    """In-memory adapter that queries skirmishes from the round store."""

    def __init__(self, round_repo: InMemoryRoundRepository) -> None:
        self._round_repo = round_repo

    def get_by_player(
        self,
        owner_id: UUID,
        opponent_id: UUID | None = None,
        last_n: int | None = None,
    ) -> list[Skirmish]:
        skirmishes = [
            skirmish
            for r in self._round_repo.list()
            for skirmish in r.skirmishes
            if owner_id in (skirmish.civ_a.id, skirmish.civ_b.id) and (
                opponent_id is None
                or opponent_id in (skirmish.civ_a.id, skirmish.civ_b.id)
            )
        ]

        if last_n is not None:
            return skirmishes[-last_n:] if last_n > 0 else []
        return skirmishes
