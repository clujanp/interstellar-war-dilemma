from uuid import UUID

from app.domain.models import AstronomyBody, Civilization, Match
from app.domain.services.match_service import MatchService
from app.domain.value_objects import Resources, Decision


class GameEngine:
    """Application service: entry point for match lifecycle"""

    def __init__(self, match_service: MatchService) -> None:
        self._match_service = match_service
        self._players: list[Civilization] = []

    def register_player(self, player: Civilization) -> None:
        """Register a civilization to participate in the next match"""
        self._players.append(player)

    def start_match(self, target_rounds: int) -> UUID:
        """Create a match with registered players and start it"""
        match = Match(
            target_rounds=target_rounds,
            civilizations=list(self._players),
        )
        match_id = self._match_service.start_match_window(match)
        return match_id

    def run_round(
        self, match_id: UUID, bodies: list[AstronomyBody],
        decisions: dict[UUID, Decision] | None = None,
    ) -> None:
        """Execute a full round: setup, apply decisions, resolve, persist"""
        self._match_service.setup_round(match_id, bodies)
        if decisions:
            for civ_id, decision in decisions.items():
                self._match_service.set_decision(match_id, civ_id, decision)
        self._match_service.resolve_round(match_id)
        self._match_service.advance_or_stop(match_id)

    def report_results(self, match_id: UUID) -> dict[str, Resources]:
        """Return cumulative scores for a match"""
        match = self._match_service.get_match(match_id)
        return dict(match.cumulative_scores)
