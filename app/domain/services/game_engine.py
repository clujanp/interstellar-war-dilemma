from app.domain.models import Civilization


class GameEngine:
    """Application service: entry point for match lifecycle."""

    def __init__(self) -> None:
        self._players: list[Civilization] = []

    def register_player(self, player: Civilization) -> None:
        """Register a civilization to participate in the next match."""
        self._players.append(player)

    @property
    def players(self) -> list[Civilization]:
        return list(self._players)
