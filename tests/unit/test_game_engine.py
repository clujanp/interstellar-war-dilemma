from unittest import TestCase

from app.adapters.db import InMemoryMatchRepository, InMemoryRoundRepository
from app.domain.models import AstronomyBody, Civilization
from app.domain.services.game_engine import GameEngine
from app.domain.services.match_service import MatchService
from app.domain.services.round_service import RoundService
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    MatchStatus,
    Resources,
)


class TestGameEngine(TestCase):
    """Tests for the GameEngine application service."""

    def setUp(self):
        """Initialize full service stack with in-memory repos."""
        self.match_repo = InMemoryMatchRepository()
        self.round_repo = InMemoryRoundRepository()
        self.round_service = RoundService()
        self.match_service = MatchService(
            round_service=self.round_service,
            match_repo=self.match_repo,
            round_repo=self.round_repo,
        )
        self.engine = GameEngine(match_service=self.match_service)

        self.body = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.civ_1 = Civilization(name="Foundation", home_astro_body=self.body)
        self.civ_2 = Civilization(name="Empire", home_astro_body=self.body)

    def test_register_player(self):
        """Verify players are registered."""
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        assert len(self.engine._players) == 2

    def test_start_match_creates_running_match(self):
        """Verify start_match creates a RUNNING match with registered players."""
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        match = self.engine.start_match(target_rounds=3)

        assert match.status == MatchStatus.RUNNING
        assert len(match.civilizations) == 2
        assert match.target_rounds == 3

    def test_run_round_with_decisions(self):
        """Verify a round executes with explicit decisions."""
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        match = self.engine.start_match(target_rounds=3)

        self.engine.run_round(match, [self.body], decisions={
            self.civ_1: Decision.COOPERATE,
            self.civ_2: Decision.DEFECT,
        })

        rounds = self.round_repo.get_by_match(match.id)
        assert len(rounds) == 1
        assert rounds[0].skirmishes[0].is_resolved

    def test_run_round_without_decisions_uses_fallback(self):
        """Verify a round uses NOT_DECIDED fallback when no decisions given."""
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        match = self.engine.start_match(target_rounds=1)

        self.engine.run_round(match, [self.body])

        rounds = self.round_repo.get_by_match(match.id)
        assert rounds[0].skirmishes[0].is_resolved

    def test_report_results_returns_scores(self):
        """Verify report_results returns cumulative scores."""
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        match = self.engine.start_match(target_rounds=1)

        self.engine.run_round(match, [self.body], decisions={
            self.civ_1: Decision.COOPERATE,
            self.civ_2: Decision.COOPERATE,
        })

        results = self.engine.report_results(match)
        assert "Foundation" in results
        assert "Empire" in results
        assert results["Foundation"] > Resources.NONE
