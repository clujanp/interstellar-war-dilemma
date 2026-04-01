from uuid import UUID

from app.domain.models import AstronomyBody, Match, Round
from app.domain.services.round_service import RoundService
from app.domain.value_objects import Decision, Resources
from app.interfaces.db import MatchRepository, RoundRepository


class MatchService:
    """Domain service that orchestrates the round loop within a match."""

    def __init__(
        self,
        round_service: RoundService,
        match_repo: MatchRepository,
        round_repo: RoundRepository,
    ) -> None:
        self._round_service = round_service
        self._match_repo = match_repo
        self._round_repo = round_repo
        self._active_round: Round | None = None

    def start_match_window(self, match: Match) -> UUID:
        """Start a match: persist and transition to RUNNING."""
        match.start()
        match_id = self._match_repo.save(match)
        return match_id

    def setup_round(
        self, match_id: UUID, astro_bodies: list[AstronomyBody]
    ) -> Round:
        """Set up a new round: advance match, generate pairings."""
        match = self._match_repo.get(match_id)
        match.advance_round()
        self._active_round = self._round_service.setup_round(match, astro_bodies)
        self._match_repo.save(match)
        return self._active_round

    def set_decision(
        self, match_id: UUID, civilization_id: UUID, decision: Decision,
    ) -> None:
        """Propagate a player's decision to their skirmish in the active round."""
        self._round_service.propagate_decision(
            self._get_active_round(), civilization_id, decision)

    def resolve_round(self, match_id: UUID) -> Round:
        """Finalize, resolve, update scores, and persist the round."""
        self._finalize_decisions()
        round = self._get_active_round()
        self._active_round = None
        self._round_service.resolve_round(round)
        self._update_scores(match_id, round)
        self._round_repo.save(match_id, round)
        return round

    def advance_or_stop(self, match_id: UUID) -> Match:
        """Check if match should continue or end. Returns updated match."""
        match = self._match_repo.get(match_id)
        if match.can_start_round:
            return match
        match.mark_completed()
        self._match_repo.save(match)
        return match

    def stop_match(self, match_id: UUID) -> Match:
        """Early stop a match."""
        match = self._match_repo.get(match_id)
        match.mark_stopped()
        self._match_repo.save(match)
        return match

    def get_match(self, match_id: UUID) -> Match:
        """Retrieve a match by id."""
        return self._match_repo.get(match_id)

    def _get_active_round(self) -> Round:
        """Return the active round or raise if none."""
        if self._active_round is None:
            raise RuntimeError("No active round.")
        return self._active_round

    def _finalize_decisions(self) -> None:
        """Apply NOT_DECIDED fallback for any missing decisions."""
        round = self._get_active_round()
        for skirmish in round.skirmishes:
            if skirmish.decision_a is None:
                skirmish.decision_a = Decision.NOT_DECIDED
            if skirmish.decision_b is None:
                skirmish.decision_b = Decision.NOT_DECIDED

    def _update_scores(self, match_id: UUID, round: Round) -> None:
        """Update cumulative scores from resolved skirmishes."""
        match = self._match_repo.get(match_id)
        for skirmish in round.skirmishes:
            name_a = skirmish.civ_a.name
            name_b = skirmish.civ_b.name
            match.cumulative_scores[name_a] = Resources(
                match.cumulative_scores.get(name_a, Resources.NONE)
                + skirmish.civ_a_resources_gained
            )
            match.cumulative_scores[name_b] = Resources(
                match.cumulative_scores.get(name_b, Resources.NONE)
                + skirmish.civ_b_resources_gained
            )
        self._match_repo.save(match)
