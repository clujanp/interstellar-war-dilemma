from collections import OrderedDict
from ulid import ULID
from ..models import CivilizationRegistration
from .interfaces import IPlayersRepo


class PlayersRepo(IPlayersRepo):
    """Concrete implementation of the players repository."""

    def __init__(self):
        self._players: OrderedDict[
            ULID, CivilizationRegistration
        ] = OrderedDict()

    def register_player(
        self, player_registration: CivilizationRegistration
    ) -> None:
        """Registers a player in the repository."""
        self._players[player_registration.id] = player_registration

    def unregister_player(self, player_id: ULID) -> None:
        """Unregisters a player from the repository using their ID."""
        self._validate_registered(player_id)
        self._players.pop(player_id, None)

    def get_player(self, player_id: ULID) -> CivilizationRegistration:
        """Retrieves a player's registration by their ID."""
        self._validate_registered(player_id)
        return self._players[player_id]

    def list_players(self) -> list[CivilizationRegistration]:
        """Lists all registered players."""
        return list(self._players.values())

    def _validate_registered(self, player_id: ULID) -> None:
        if player_id not in self._players:
            raise KeyError(f"Player with ID {player_id} not found.")
