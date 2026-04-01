from unittest import TestCase

from app.domain.models import AstronomyBody, Civilization, Match
from app.domain.services.round_service import RoundService
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    MatchStatus,
    Resources,
)


class TestRoundService(TestCase):
    """Tests for the RoundService domain service."""

    def setUp(self):
        """Initialize test fixtures with 4 civilizations (even count)."""
        self.body_a = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.body_b = AstronomyBody(
            name="Beta", type=AstroType.MOON, resources=Resources(6))

        self.civ_1 = Civilization(name="Foundation", home_astro_body=self.body_a)
        self.civ_2 = Civilization(name="Empire", home_astro_body=self.body_a)
        self.civ_3 = Civilization(name="Alliance", home_astro_body=self.body_b)
        self.civ_4 = Civilization(name="Guild", home_astro_body=self.body_b)

        self.match = Match(
            status=MatchStatus.RUNNING,
            target_rounds=5,
            current_round=1,
            civilizations=[self.civ_1, self.civ_2, self.civ_3, self.civ_4],
        )
        self.service = RoundService()

    def test_setup_round_generates_correct_number_of_skirmishes(self):
        """Verify 4 civilizations produce 2 skirmishes (1 per pair)."""
        round = self.service.setup_round(self.match, [self.body_a])
        assert len(round.skirmishes) == 2
        assert round.number == 1

    def test_setup_round_each_civ_appears_once(self):
        """Verify each civilization appears in exactly one skirmish."""
        round = self.service.setup_round(self.match, [self.body_a])
        civ_ids = []
        for s in round.skirmishes:
            civ_ids.extend([s.civ_a.id, s.civ_b.id])
        assert len(civ_ids) == len(set(civ_ids))

    def test_setup_round_assigns_bodies_round_robin(self):
        """Verify astronomical bodies are assigned cyclically."""
        round = self.service.setup_round(self.match, [self.body_a, self.body_b])
        bodies = [s.astronomical_object for s in round.skirmishes]
        assert bodies == [self.body_a, self.body_b]

    def test_propagate_decision_sets_on_correct_side(self):
        """Verify decision is set on the correct civ_a or civ_b slot."""
        round = self.service.setup_round(self.match, [self.body_a])
        self.service.propagate_decision(round, self.civ_1.id, Decision.COOPERATE)

        for s in round.skirmishes:
            if s.civ_a.id == self.civ_1.id:
                assert s.decision_a == Decision.COOPERATE
            elif s.civ_b.id == self.civ_1.id:
                assert s.decision_b == Decision.COOPERATE

    def test_propagate_decision_does_not_affect_other_civs(self):
        """Verify that propagating a decision does not touch other civilizations."""
        round = self.service.setup_round(self.match, [self.body_a])
        self.service.propagate_decision(round, self.civ_1.id, Decision.DEFECT)

        for s in round.skirmishes:
            if s.civ_a.id != self.civ_1.id:
                assert s.decision_a is None
            if s.civ_b.id != self.civ_1.id:
                assert s.decision_b is None

    def test_resolve_round_resolves_all_skirmishes(self):
        """Verify all skirmishes are resolved after resolve_round."""
        round = self.service.setup_round(self.match, [self.body_a])
        for civ in self.match.civilizations:
            self.service.propagate_decision(round, civ.id, Decision.COOPERATE)

        self.service.resolve_round(round)

        for s in round.skirmishes:
            assert s.is_resolved

    def test_resolve_round_returns_same_round(self):
        """Verify resolve_round returns the same round object."""
        round = self.service.setup_round(self.match, [self.body_a])
        for civ in self.match.civilizations:
            self.service.propagate_decision(round, civ.id, Decision.DEFECT)

        result = self.service.resolve_round(round)
        assert result is round
