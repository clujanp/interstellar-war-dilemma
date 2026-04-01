from app.domain.models import AstronomyBody, Civilization, Match, Round
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

    def start_match_window(self, match: Match) -> Match:
        """Start a match: transition to RUNNING and persist."""
        match.start()
        self._match_repo.save(match)
        return match

    def setup_round(
        self, match: Match, astro_bodies: list[AstronomyBody]
    ) -> Round:
        """Set up a new round: advance match, generate pairings."""
        match.advance_round()
        self._active_round = self._round_service.setup_round(match, astro_bodies)
        self._match_repo.save(match)
        return self._active_round

    def set_decision(
        self, civilization: Civilization, decision: Decision,
    ) -> None:
        """Propagate a player's decision to their skirmish in the active round."""
        self._round_service.propagate_decision(
            self._get_active_round(), civilization, decision)

    def resolve_round(self, match: Match) -> Round:
        """Finalize, resolve, update scores, and persist the round."""
        self._finalize_decisions()
        round = self._get_active_round()
        self._active_round = None
        self._round_service.resolve_round(round)
        self._update_scores(match, round)
        self._round_repo.save(match.id, round)
        return round

    def advance_or_stop(self, match: Match) -> Match:
        """Check if match should continue or end."""
        if match.can_start_round:
            return match
        match.mark_completed()
        self._match_repo.save(match)
        return match

    def stop_match(self, match: Match) -> Match:
        """Early stop a match."""
        match.mark_stopped()
        self._match_repo.save(match)
        return match

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

    def _update_scores(self, match: Match, round: Round) -> None:
        """Update cumulative scores from resolved skirmishes."""
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
