from unittest import TestCase

from app.adapters.db import InMemoryMatchRepository, InMemoryRoundRepository
from app.domain.models import AstronomyBody, Civilization
from app.domain.services.match_service import MatchSession
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    MatchStatus,
    Resources,
)


class TestMatchSession(TestCase):
    """Tests for the MatchSession domain service."""

    def setUp(self):
        """Initialize repos, and test data."""
        self.match_repo = InMemoryMatchRepository()
        self.round_repo = InMemoryRoundRepository()

        self.body = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.civ_1 = Civilization(name="Foundation", home=self.body)
        self.civ_2 = Civilization(name="Empire", home=self.body)

    def _make_session(self, target_rounds=3):
        return MatchSession(
            civilizations=[self.civ_1, self.civ_2],
            target_rounds=target_rounds,
            match_repo=self.match_repo,
            round_repo=self.round_repo,
        )

    def test_constructor_starts_match(self):
        """Verify match is RUNNING after construction."""
        session = self._make_session()
        assert session.match.status == MatchStatus.RUNNING
        assert self.match_repo.get(session.match.id) is session.match

    def test_iteration_yields_round_contexts(self):
        """Verify iterating yields one RoundContext per round."""
        session = self._make_session()
        count = 0
        for round_ctx in session:
            with round_ctx:
                round_ctx.set_decision(self.civ_1, Decision.COOPERATE)
                round_ctx.set_decision(self.civ_2, Decision.COOPERATE)
            count += 1
        assert count == 3
        assert session.match.status == MatchStatus.COMPLETED

    def test_round_advances_current_round(self):
        """Verify each round increments current_round."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                pass
        assert session.match.current_round == 3

    def test_finalize_decisions_fills_not_decided(self):
        """Verify missing decisions are filled with NOT_DECIDED."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                pass  # no decisions
            skirmish = round_ctx.round.skirmishes[0]
            assert skirmish.decision_a == Decision.NOT_DECIDED
            assert skirmish.decision_b == Decision.NOT_DECIDED
            break

    def test_resolve_round_persists(self):
        """Verify resolved rounds are persisted."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                round_ctx.set_decision(self.civ_1, Decision.COOPERATE)
                round_ctx.set_decision(self.civ_2, Decision.COOPERATE)

        stored_rounds = self.round_repo.list_by_match(session.match.id)
        assert len(stored_rounds) == 3
        for r in stored_rounds:
            assert r.skirmishes[0].is_resolved

    def test_cumulative_scores_update(self):
        """Verify cumulative scores are updated after resolution."""
        session = self._make_session()
        for round_ctx in session:
            with round_ctx:
                round_ctx.set_decision(self.civ_1, Decision.COOPERATE)
                round_ctx.set_decision(self.civ_2, Decision.COOPERATE)

        assert session.match.cumulative_scores["Foundation"] > Resources.NONE
        assert session.match.cumulative_scores["Empire"] > Resources.NONE

    def test_stop_match_transitions_to_stopped(self):
        """Verify stop_match transitions match to STOPPED."""
        session = self._make_session()
        match = session.stop_match()
        assert match.status == MatchStatus.STOPPED

    def test_stop_match_breaks_iteration(self):
        """Verify stopping a match prevents further rounds."""
        session = self._make_session()
        count = 0
        for round_ctx in session:
            with round_ctx:
                pass
            count += 1
            if count == 1:
                session.stop_match()
                break
        assert count == 1
        assert session.match.status == MatchStatus.STOPPED
