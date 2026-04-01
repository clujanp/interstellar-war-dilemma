from app.domain.models import AstronomyBody, Civilization, Match
from app.domain.services.match_service import MatchService
from app.domain.value_objects import Resources, Decision


class GameEngine:
    """Application service: entry point for match lifecycle."""

    def __init__(self, match_service: MatchService) -> None:
        self._match_service = match_service
        self._players: list[Civilization] = []

    def register_player(self, player: Civilization) -> None:
        """Register a civilization to participate in the next match."""
        self._players.append(player)

    def start_match(self, target_rounds: int) -> Match:
        """Create a match with registered players and start it."""
        match = Match(
            target_rounds=target_rounds,
            civilizations=list(self._players),
        )
        return self._match_service.start_match_window(match)

    def run_round(
        self,
        match: Match,
        bodies: list[AstronomyBody],
        decisions: dict[Civilization, Decision] | None = None,
    ) -> None:
        """Execute a full round: setup, apply decisions, resolve, persist."""
        self._match_service.setup_round(match, bodies)
        if decisions:
            for civ, decision in decisions.items():
                self._match_service.set_decision(civ, decision)
        self._match_service.resolve_round(match)
        self._match_service.advance_or_stop(match)

    def report_results(self, match: Match) -> dict[str, Resources]:
        """Return cumulative scores for a match."""
        return dict(match.cumulative_scores)
