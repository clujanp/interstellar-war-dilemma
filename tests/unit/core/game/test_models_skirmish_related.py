from unittest import TestCase
from app.core.domain.models.entities import AstroBody, Skirmish
from app.core.domain.value_objects import (
    AstroBodyProduction, ColonizeCost, Efficiency, Resources, Decision)
from app.core.game.models import CivilizationRegistration, SkirmishRelated


class TestSkirmishRelatedModel(TestCase):
    """Test suite for the SkirmishRelatedModel class."""

    def setUp(self):
        """Set up test environment for each test."""
        self.player_1 = CivilizationRegistration(
            name="Player1",
            resources=Resources(100),
            callback=lambda *_, **__: Decision.ATTACK,
        )
        self.player_2 = CivilizationRegistration(
            name="Player2",
            resources=Resources(100),
            callback=lambda *_, **__: Decision.COOPERATE,
        )
        self.astro = AstroBody(
            name="Trantor",
            kind="planet",
            colonize_cost=ColonizeCost.HOSTILE,
            production=AstroBodyProduction.HIGH,
        )
        self.skirmish = Skirmish(
            civilizations=(self.player_1, self.player_2),
            astro_body=self.astro,
        )

    def test_initialization(self):
        """Test that a SkirmishRelatedModel instance can be initialized."""
        skirmish = SkirmishRelated(
            owner=self.player_1,
            skirmish=self.skirmish,
        )
        assert skirmish.owner == self.player_1
        assert skirmish.skirmish == self.skirmish
        assert skirmish.opponent == "Player2"
        assert skirmish.astro.name == "Trantor"
        assert skirmish.astro.kind == "planet"
        assert skirmish.astro.cost == ColonizeCost.HOSTILE
        assert skirmish.astro.production == AstroBodyProduction.HIGH

        with self.subTest("skirmish not resolved yet"):
            assert skirmish.decision == Decision.NONE
            assert skirmish.opponent_decision == Decision.NONE
            assert skirmish.result is None
            assert skirmish.gain_factor == Efficiency.NONE

    def test_when_skirmish_resolved(self):
        """Test the behavior when the skirmish is resolved."""
        self.skirmish.decisions = [Decision.ATTACK, Decision.COOPERATE]
        self.skirmish.resolve()
        skirmish = SkirmishRelated(
            owner=self.player_1,
            skirmish=self.skirmish,
        )

        assert skirmish.decision == Decision.ATTACK
        assert skirmish.opponent_decision == Decision.COOPERATE
        assert skirmish.result is not None
        assert skirmish.gain_factor == Efficiency.TREASON
