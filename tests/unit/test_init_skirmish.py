from random import choice
from unittest import TestCase
from app.core.domain.models import AstroBody, Civilization, Skirmish
from app.core.domain.value_objects import (
    AstroBodyProduction, AstroKind, ColonizeCost, Decision, Resources,
    SkirmishStatus,)


class TestInitSkirmish(TestCase):
    """Unit test for the initialization of a skirmish."""

    def setUp(self):
        self.civ_a = Civilization(name="Civ A", resources=Resources(10))
        self.civ_b = Civilization(name="Civ B", resources=Resources(10))
        self.astro_bodies = [
            AstroBody(
                name=AstroBody.name_generator(),
                kind=choice(list(AstroKind)),
                colonize_cost=choice(list(ColonizeCost)),
                production=choice(list(AstroBodyProduction)),
            )
        ]

    def test_init_skirmish(self):
        """Test the initialization of a skirmish."""
        skirmish = Skirmish(
            civilizations=(self.civ_a, self.civ_b),
            astro_body=self.astro_bodies[0],
        )
        assert skirmish.civilizations == (self.civ_a, self.civ_b)
        assert skirmish.astro_body == self.astro_bodies[0]
        assert skirmish.decisions == [Decision.NONE, Decision.NONE]
        assert skirmish.result is None
        assert skirmish.production_participation is None
        assert skirmish.status == SkirmishStatus.ONGOING
