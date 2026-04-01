from unittest import TestCase

from app.domain.models import AstronomyBody, Civilization
from app.domain.services.game_engine import GameEngine
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Resources,
)


class TestGameEngine(TestCase):
    """Tests for the GameEngine application service."""

    def setUp(self):
        """Initialize engine and test data."""
        self.engine = GameEngine()

        self.body = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.civ_1 = Civilization(name="Foundation", home=self.body)
        self.civ_2 = Civilization(name="Empire", home=self.body)

    def test_register_player(self):
        """Verify players are registered."""
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        assert len(self.engine.players) == 2

    def test_players_returns_copy(self):
        """Verify players property returns a copy."""
        self.engine.register_player(self.civ_1)
        players = self.engine.players
        players.append(self.civ_2)
        assert len(self.engine.players) == 1
