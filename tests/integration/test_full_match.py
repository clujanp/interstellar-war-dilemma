from unittest import TestCase
from unittest.mock import patch

from app.adapters.db import (
    InMemoryMatchRepository,
    InMemoryRoundRepository,
    InMemorySkirmishQueryRepository,
)
from app.domain.models import AstronomyBody, Civilization
from app.domain.services.game_engine import GameEngine
from app.domain.services.match_service import MatchSession
from app.domain.services.memories_service import MemoriesService
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    MatchStatus,
    Resources,
    Resolution,
)


class TestFullMatch(TestCase):
    """Integration test: full multi-round match with all services wired together."""

    def setUp(self):
        """Wire up the full service stack with in-memory adapters."""
        self.match_repo = InMemoryMatchRepository()
        self.round_repo = InMemoryRoundRepository()
        self.skirmish_repo = InMemorySkirmishQueryRepository(self.round_repo)

        self.memories_service = MemoriesService(self.skirmish_repo)
        self.engine = GameEngine()

        self.terminus = AstronomyBody(
            name="Terminus", type=AstroType.PLANET, resources=Resources(1))
        self.trantor = AstronomyBody(
            name="Trantor", type=AstroType.PLANET, resources=Resources(10))
        self.civ_1 = Civilization(name="Foundation", home=self.terminus)
        self.civ_2 = Civilization(name="Empire", home=self.trantor)
        
        # patches
        self._patch_astro = patch(
            "app.domain.services.round_context"
            ".RoundContext._generate_astro_bodies",
            return_value=[AstronomyBody(
                name="Disputed",
                type=AstroType.PLANET,
                resources=Resources(6),
            )],
        )
        self._patch_shuffle = patch(
            "app.domain.services.round_context"
            ".RoundContext._suffle_civilizations",
            side_effect=lambda civs: civs,
        )
        self._patch_astro.start()
        self._patch_shuffle.start()
        
    def tearDown(self):
        self._patch_astro.stop()
        self._patch_shuffle.stop()

    def _make_session(self, target_rounds: int) -> MatchSession:
        self.engine.register_player(self.civ_1)
        self.engine.register_player(self.civ_2)
        return MatchSession(
            civilizations=self.engine.players,
            target_rounds=target_rounds,
            match_repo=self.match_repo,
            round_repo=self.round_repo,
        )

    def test_multi_round_match_completes(self):
        """Run a 3-round match with decisions and verify completion."""
        round_decisions = [
            (Decision.COOPERATE, Decision.COOPERATE),
            (Decision.DEFECT, Decision.COOPERATE),
            (Decision.COOPERATE, Decision.DEFECT),
        ]

        session = self._make_session(target_rounds=3)
        for round_ctx, (d1, d2) in zip(session, round_decisions):
            with round_ctx:
                round_ctx.set_decision(self.civ_1, d1)
                round_ctx.set_decision(self.civ_2, d2)

        assert session.match.status == MatchStatus.COMPLETED
        assert session.match.current_round == 3
        # COOPERATION=3/6*6=3, BETRAYAL winner=5/6*6=5, loser=0
        assert session.match.cumulative_scores == {
            "Foundation": Resources(9),   # home(1) + 3 + 5 + 0
            "Empire": Resources(18),      # home(10) + 3 + 0 + 5
        }

        rounds = self.round_repo.list_by_match(session.match.id)
        assert len(rounds) == 3
        expected_resolutions = [
            Resolution.COOPERATION,
            Resolution.BETRAYAL_A,
            Resolution.BETRAYAL_B,
        ]
        for r, expected in zip(rounds, expected_resolutions):
            assert r.match.id == session.match.id
            assert len(r.skirmishes) == 1
            assert r.skirmishes[0].resolution == expected

    def test_cumulative_scores_accumulate(self):
        """Verify scores accumulate correctly across rounds."""
        session = self._make_session(target_rounds=2)
        for round_ctx in session:
            with round_ctx:
                round_ctx.set_decision(self.civ_1, Decision.COOPERATE)
                round_ctx.set_decision(self.civ_2, Decision.COOPERATE)

        # home(1) + 2*COOPERATION(3) = 7, home(10) + 2*3 = 16
        assert session.match.cumulative_scores == {
            "Foundation": Resources(7),
            "Empire": Resources(16),
        }

    def test_deadline_fallback_in_full_match(self):
        """Verify match completes even when no decisions are submitted."""
        session = self._make_session(target_rounds=2)
        for round_ctx in session:
            with round_ctx:
                pass

        assert session.match.status == MatchStatus.COMPLETED

    def test_early_stop_prevents_more_rounds(self):
        """Verify early stop prevents starting new rounds."""
        session = self._make_session(target_rounds=5)
        count = 0
        for round_ctx in session:
            with round_ctx:
                round_ctx.set_decision(self.civ_1, Decision.COOPERATE)
                round_ctx.set_decision(self.civ_2, Decision.COOPERATE)
            count += 1
            if count == 1:
                session.stop_match()
                break

        assert session.match.status == MatchStatus.STOPPED
        rounds = self.round_repo.list_by_match(session.match.id)
        assert len(rounds) == 1

    def test_memories_service_reads_history_after_match(
        self  
    ):
        """Verify MemoriesService can query skirmish history after rounds complete."""
        round_decisions = [
            (Decision.COOPERATE, Decision.DEFECT),
            (Decision.DEFECT, Decision.DEFECT),
        ]

        session = self._make_session(target_rounds=2)
        for round_ctx, (d1, d2) in zip(session, round_decisions):
            with round_ctx:
                round_ctx.set_decision(self.civ_1, d1)
                round_ctx.set_decision(self.civ_2, d2)

        history = self.memories_service.get_skirmish_history(self.civ_1)
        assert len(history) == 2

        filtered = self.memories_service.get_skirmish_history(
            self.civ_1, opponent=self.civ_2)
        assert len(filtered) == 2

        last_one = self.memories_service.get_skirmish_history(
            self.civ_1, last_n=1)
        assert len(last_one) == 1
