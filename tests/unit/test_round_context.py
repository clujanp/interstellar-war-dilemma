from unittest import TestCase

from app.adapters.db import InMemoryMatchRepository, InMemoryRoundRepository
from app.domain.models import AstronomyBody, Civilization
from app.domain.services.match_service import MatchSession
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    Resources,
)


class TestRoundContext(TestCase):
    """Tests for the RoundContext context manager."""

    def setUp(self):
        """Initialize service stack and test data."""
        self.match_repo = InMemoryMatchRepository()
        self.round_repo = InMemoryRoundRepository()

        self.body = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.civ_1 = Civilization(name="Foundation", home=self.body)
        self.civ_2 = Civilization(name="Empire", home=self.body)
        self.civ_3 = Civilization(name="Alliance", home=self.body)
        self.civ_4 = Civilization(name="Guild", home=self.body)

    def _make_session(self, target_rounds=5):
        return MatchSession(
            civilizations=[self.civ_1, self.civ_2, self.civ_3, self.civ_4],
            target_rounds=target_rounds,
            match_repo=self.match_repo,
            round_repo=self.round_repo,
        )

    def test_setup_generates_correct_number_of_skirmishes(self):
        """Verify 4 civilizations produce 2 skirmishes."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                assert len(round_ctx.round.skirmishes) == 2
            break

    def test_each_civ_appears_once(self):
        """Verify each civilization appears in exactly one skirmish."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                civ_ids = []
                for s in round_ctx.round.skirmishes:
                    civ_ids.extend([s.civ_a.id, s.civ_b.id])
                assert len(civ_ids) == len(set(civ_ids))
            break

    def test_generates_astro_bodies_per_pairing(self):
        """Verify each skirmish gets its own generated AstronomyBody."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                bodies = [s.astronomical_object for s in round_ctx.round.skirmishes]
                assert len(bodies) == 2
                assert bodies[0].id != bodies[1].id
            break

    def test_set_decision_on_correct_side(self):
        """Verify decision is set on the correct civ_a or civ_b slot."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                round_ctx.set_decision(self.civ_1, Decision.COOPERATE)
                for s in round_ctx.round.skirmishes:
                    if s.civ_a.id == self.civ_1.id:
                        assert s.decision_a == Decision.COOPERATE
                    elif s.civ_b.id == self.civ_1.id:
                        assert s.decision_b == Decision.COOPERATE
            break

    def test_resolves_all_skirmishes_on_exit(self):
        """Verify all skirmishes are resolved after exiting context."""
        session = self._make_session()
        civs = [self.civ_1, self.civ_2, self.civ_3, self.civ_4]
        for round_ctx in session:
            with round_ctx:
                for civ in civs:
                    round_ctx.set_decision(civ, Decision.COOPERATE)
            for s in round_ctx.round.skirmishes:
                assert s.is_resolved
            break

    def test_fallback_not_decided_on_exit(self):
        """Verify missing decisions get NOT_DECIDED on exit."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                pass  # no decisions
            for s in round_ctx.round.skirmishes:
                assert s.is_resolved
                assert s.decision_a == Decision.NOT_DECIDED
                assert s.decision_b == Decision.NOT_DECIDED
            break

    def test_round_not_accessible_before_enter(self):
        """Verify accessing round before __enter__ raises."""
        session = self._make_session()
        for round_ctx in session:
            with self.assertRaises(RuntimeError):
                _ = round_ctx.round
            with round_ctx:
                pass
            break
