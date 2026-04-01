from unittest import TestCase
from uuid import uuid4

from app.adapters.db import InMemoryRoundRepository, InMemorySkirmishQueryRepository
from app.domain.models import AstronomyBody, Civilization, Round, Skirmish
from app.domain.services.memories_service import MemoriesService
from app.domain.value_objects import (
    AstronomicObjectType as AstroType,
    Decision,
    Resources,
)


class TestMemoriesService(TestCase):
    """Tests for the MemoriesService query service."""

    def setUp(self):
        """Initialize repos, service, and test data."""
        self.round_repo = InMemoryRoundRepository()
        self.skirmish_repo = InMemorySkirmishQueryRepository(self.round_repo)
        self.service = MemoriesService(self.skirmish_repo)

        self.body = AstronomyBody(
            name="Alpha", type=AstroType.PLANET, resources=Resources(12))
        self.civ_1 = Civilization(name="Foundation", home_astro_body=self.body)
        self.civ_2 = Civilization(name="Empire", home_astro_body=self.body)
        self.civ_3 = Civilization(name="Alliance", home_astro_body=self.body)

    def _make_resolved_skirmish(self, civ_a, civ_b):
        """Create a resolved skirmish between two civilizations."""
        s = Skirmish(
            civ_a=civ_a,
            civ_b=civ_b,
            astronomical_object=self.body,
            decision_a=Decision.COOPERATE,
            decision_b=Decision.DEFECT,
        )
        s.resolve()
        return s

    def test_returns_empty_when_no_history(self):
        """Verify empty list when no skirmishes exist."""
        result = self.service.get_skirmish_history(self.civ_1)
        assert result == []

    def test_returns_skirmishes_for_owner(self):
        """Verify skirmishes involving the owner are returned."""
        s1 = self._make_resolved_skirmish(self.civ_1, self.civ_2)
        s2 = self._make_resolved_skirmish(self.civ_2, self.civ_3)
        match_id = uuid4()
        self.round_repo.save(match_id, Round(number=1, skirmishes=[s1, s2]))

        result = self.service.get_skirmish_history(self.civ_1)
        assert len(result) == 1
        assert result[0] is s1

    def test_filters_by_opponent(self):
        """Verify filtering by opponent civilization."""
        s1 = self._make_resolved_skirmish(self.civ_1, self.civ_2)
        s2 = self._make_resolved_skirmish(self.civ_1, self.civ_3)
        match_id = uuid4()
        self.round_repo.save(match_id, Round(number=1, skirmishes=[s1, s2]))

        result = self.service.get_skirmish_history(self.civ_1, opponent=self.civ_3)
        assert len(result) == 1
        assert result[0] is s2

    def test_limits_with_last_n(self):
        """Verify last_n limits the results."""
        s1 = self._make_resolved_skirmish(self.civ_1, self.civ_2)
        s2 = self._make_resolved_skirmish(self.civ_1, self.civ_3)
        match_id = uuid4()
        self.round_repo.save(match_id, Round(number=1, skirmishes=[s1]))
        self.round_repo.save(match_id, Round(number=2, skirmishes=[s2]))

        result = self.service.get_skirmish_history(self.civ_1, last_n=1)
        assert len(result) == 1
        assert result[0] is s2
