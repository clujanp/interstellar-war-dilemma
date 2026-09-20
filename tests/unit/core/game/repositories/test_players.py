from collections import OrderedDict
from random import choice
from unittest import TestCase
from app.core.game.repositories.players import PlayersRepo
from app.core.game.models import CivilizationRegistration
from app.core.game.repositories.interfaces import IPlayersRepo
from app.core.domain.value_objects import Resources, Decision


class TestPlayersRepo(TestCase):
    """Unit tests for the PlayersRepo class."""

    def setUp(self):
        self.player_1 = CivilizationRegistration(
            name="Player1",
            resources=Resources(100),
            callback=lambda *_, **__: choice([
                Decision.COOPERATE, Decision.ATTACK]),
        )
        self.player_2 = CivilizationRegistration(
            name="self.player_2",
            resources=Resources(100),
            callback=lambda *_, **__: choice([
                Decision.COOPERATE, Decision.ATTACK]),
        )

    def test_interface(self):
        """Test that PlayersRepo implements the IPlayersRepo interface."""
        assert issubclass(PlayersRepo, IPlayersRepo)

    def test_register_player(self):
        """Test that a player can be registered in the repository."""
        repo = PlayersRepo()
        repo.register_player(self.player_1)
        # pylint: disable=protected-access
        assert repo._players == OrderedDict([
            (self.player_1.id, self.player_1)
        ])

    def test_register_multiple_players(self):
        """Test that multiple players can be registered in the repository."""
        repo = PlayersRepo()
        repo.register_player(self.player_1)
        repo.register_player(self.player_2)
        # pylint: disable=protected-access
        assert repo._players == OrderedDict([
            (self.player_1.id, self.player_1),
            (self.player_2.id, self.player_2)
        ])

    def test_unregister_player(self):
        """Test that a player can be unregistered from the repository."""
        repo = PlayersRepo()
        repo.register_player(self.player_1)
        repo.unregister_player(self.player_1.id)
        # pylint: disable=protected-access
        assert repo._players == OrderedDict()

    def test_unregister_nonexistent_player(self):
        """Test that unregistering a nonexistent player raises a KeyError."""
        repo = PlayersRepo()
        with self.assertRaises(KeyError) as err:
            repo.unregister_player("nonexistent_id")
        assert "Player with ID nonexistent_id not found." in str(err.exception)

    def test_get_player(self):
        """Test that a player can be retrieved from the repository."""
        repo = PlayersRepo()
        repo.register_player(self.player_1)
        retrieved_player = repo.get_player(self.player_1.id)
        assert retrieved_player == self.player_1

    def test_get_nonexistent_player(self):
        """Test that retrieving a nonexistent player returns None."""
        repo = PlayersRepo()
        with self.assertRaises(KeyError) as err:
            repo.get_player("nonexistent_id")
        assert "Player with ID nonexistent_id not found." in str(err.exception)

    def test_list_players(self):
        """Test that all registered players can be listed."""
        repo = PlayersRepo()
        repo.register_player(self.player_1)
        repo.register_player(self.player_2)
        players_list = repo.list_players()
        assert players_list == [self.player_1, self.player_2]
