from uuid import UUID, uuid4

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
        if match.id is None:
            match.id = uuid4()
        self._store[match.id] = match
        return match.id

    def get(self, match_id: UUID) -> Match:
        match = self._store.get(match_id)
        if match is None:
            raise KeyError(f"Match '{match_id}' not found.")
        return match


class InMemoryRoundRepository(RoundRepository):
    """In-memory adapter for Round persistence, keyed by match_id."""

    def __init__(self) -> None:
        self._store: dict[UUID, list[Round]] = {}

    def save(self, match_id: UUID, round: Round) -> None:
        self._store.setdefault(match_id, []).append(round)

    def get_by_match(self, match_id: UUID) -> list[Round]:
        return list(self._store.get(match_id, []))

    def get(self, match_id: UUID, round_number: int) -> Round:
        for r in self._store.get(match_id, []):
            if r.number == round_number:
                return r
        raise KeyError(
            f"Round {round_number} not found for match '{match_id}'.")


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
            for rounds in self._round_repo._store.values()
            for r in rounds
            for skirmish in r.skirmishes
            if owner_id in (skirmish.civ_a.id, skirmish.civ_b.id) and (
                opponent_id is None
                or opponent_id in (skirmish.civ_a.id, skirmish.civ_b.id)
            )
        ]

        if last_n is not None:
            return skirmishes[-last_n:] if last_n > 0 else []
        return skirmishes
