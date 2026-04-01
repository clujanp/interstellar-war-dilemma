from unittest import TestCase

from app.adapters.db import InMemoryMatchRepository, InMemoryRoundRepository
from app.domain.models import AstronomyBody, Civilization, Match
from app.domain.services.match_service import MatchService
from app.domain.services.round_service import RoundService
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    MatchStatus,
    Resources,
)


class TestMatchService(TestCase):
    """Tests for the MatchService domain service."""

    def setUp(self):
        """Initialize repos, services, and test data."""
        self.match_repo = InMemoryMatchRepository()
        self.round_repo = InMemoryRoundRepository()
        self.round_service = RoundService()
        self.service = MatchService(
            round_service=self.round_service,
            match_repo=self.match_repo,
            round_repo=self.round_repo,
        )

        self.body = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.civ_1 = Civilization(name="Foundation", home_astro_body=self.body)
        self.civ_2 = Civilization(name="Empire", home_astro_body=self.body)

        self.match = Match(
            target_rounds=3,
            civilizations=[self.civ_1, self.civ_2],
        )

    def test_start_match_window_transitions_to_running(self):
        """Verify match transitions to RUNNING and gets persisted."""
        match_id = self.service.start_match_window(self.match)
        stored = self.match_repo.get(match_id)
        assert stored.status == MatchStatus.RUNNING

    def test_setup_round_advances_current_round(self):
        """Verify setup_round increments match current_round."""
        match_id = self.service.start_match_window(self.match)
        self.service.setup_round(match_id, [self.body])
        match = self.match_repo.get(match_id)
        assert match.current_round == 1

    def test_setup_round_creates_skirmishes(self):
        """Verify setup_round creates a round with skirmishes."""
        match_id = self.service.start_match_window(self.match)
        round = self.service.setup_round(match_id, [self.body])
        assert len(round.skirmishes) == 1

    def test_set_decision_propagates_to_skirmish(self):
        """Verify set_decision sets decision on the correct skirmish."""
        match_id = self.service.start_match_window(self.match)
        round = self.service.setup_round(match_id, [self.body])
        self.service.set_decision(match_id, self.civ_1.id, Decision.COOPERATE)

        skirmish = round.skirmishes[0]
        if skirmish.civ_a.id == self.civ_1.id:
            assert skirmish.decision_a == Decision.COOPERATE
        else:
            assert skirmish.decision_b == Decision.COOPERATE

    def test_finalize_decisions_fills_not_decided(self):
        """Verify missing decisions are filled with NOT_DECIDED."""
        match_id = self.service.start_match_window(self.match)
        round = self.service.setup_round(match_id, [self.body])
        self.service._finalize_decisions()

        skirmish = round.skirmishes[0]
        assert skirmish.decision_a == Decision.NOT_DECIDED
        assert skirmish.decision_b == Decision.NOT_DECIDED

    def test_resolve_round_persists_and_resolves(self):
        """Verify resolve_round resolves skirmishes and persists the round."""
        match_id = self.service.start_match_window(self.match)
        self.service.setup_round(match_id, [self.body])
        self.service.set_decision(match_id, self.civ_1.id, Decision.COOPERATE)
        self.service.set_decision(match_id, self.civ_2.id, Decision.COOPERATE)

        round = self.service.resolve_round(match_id)

        assert round.skirmishes[0].is_resolved
        stored_rounds = self.round_repo.get_by_match(match_id)
        assert len(stored_rounds) == 1

    def test_resolve_round_updates_cumulative_scores(self):
        """Verify cumulative scores are updated after resolution."""
        match_id = self.service.start_match_window(self.match)
        self.service.setup_round(match_id, [self.body])
        self.service.set_decision(match_id, self.civ_1.id, Decision.COOPERATE)
        self.service.set_decision(match_id, self.civ_2.id, Decision.COOPERATE)
        self.service.resolve_round(match_id)

        match = self.match_repo.get(match_id)
        assert match.cumulative_scores["Foundation"] > Resources.NONE
        assert match.cumulative_scores["Empire"] > Resources.NONE

    def test_resolve_round_with_no_decisions_uses_fallback(self):
        """Verify round resolves with NOT_DECIDED fallback when no decisions submitted."""
        match_id = self.service.start_match_window(self.match)
        self.service.setup_round(match_id, [self.body])
        round = self.service.resolve_round(match_id)

        assert round.skirmishes[0].is_resolved

    def test_advance_or_stop_continues_when_rounds_remain(self):
        """Verify match stays RUNNING when rounds remain."""
        match_id = self.service.start_match_window(self.match)
        self.service.setup_round(match_id, [self.body])
        self.service.resolve_round(match_id)

        match = self.service.advance_or_stop(match_id)
        assert match.status == MatchStatus.RUNNING

    def test_advance_or_stop_completes_when_all_rounds_done(self):
        """Verify match transitions to COMPLETED when all rounds are done."""
        match_id = self.service.start_match_window(self.match)
        for _ in range(3):
            self.service.setup_round(match_id, [self.body])
            self.service.resolve_round(match_id)

        match = self.service.advance_or_stop(match_id)
        assert match.status == MatchStatus.COMPLETED

    def test_stop_match_transitions_to_stopped(self):
        """Verify stop_match transitions match to STOPPED."""
        match_id = self.service.start_match_window(self.match)
        match = self.service.stop_match(match_id)
        assert match.status == MatchStatus.STOPPED
