from unittest import TestCase

from app.domain.exceptions import MemoriesValidationExcept
from app.domain.models import AstronomyBody, Civilization, Skirmish
from app.domain.services.memories import Memories
from app.domain.value_objects import AstronomicObjectType as AstroType
from app.domain.value_objects import Decision, Resources


class TestMemories(TestCase):
    """Tests for the Memories service."""
    def setUp(self):
        """Initialize test fixtures with civilizations and memories instance."""
        self.home = AstronomyBody(
            name="Siwenna", type=AstroType.PLANET, resources=Resources(12))
        self.owner = Civilization(name="Foundation", home_astro_body=self.home)
        self.opponent = Civilization(name="Empire", home_astro_body=self.home)
        self.other = Civilization(name="Alliance", home_astro_body=self.home)
        self.other_2 = Civilization(name="Guild", home_astro_body=self.home)
        self.memories = Memories(owner=self.owner)

    def _resolved_skirmish(
        self, civ_a: Civilization, civ_b: Civilization
    ) -> Skirmish:
        """Create and resolve a skirmish between two civilizations."""
        skirmish = Skirmish(
            civ_a=civ_a,
            civ_b=civ_b,
            astronomical_object=self.home,
            decision_a=Decision.COOPERATE,
            decision_b=Decision.DEFECT,
        )
        skirmish.resolve()
        return skirmish

    def test_record_skirmish_rejects_unresolved(self):
        """Verify that recording an unresolved skirmish raises validation error."""
        with self.assertRaises(MemoriesValidationExcept) as context:
            self.memories.record_skirmish(Skirmish(
                civ_a=self.owner,
                civ_b=self.opponent,
                astronomical_object=self.home,
            ))
        assert "Only resolved skirmishes can be recorded in memories." in str(
            context.exception)

    def test_record_skirmish_rejects_unrelated(self):
        """Verify that recording a skirmish without the owner raises validation error."""
        skirmish = self._resolved_skirmish(self.other, self.other_2)

        with self.assertRaises(MemoriesValidationExcept) as context:
            self.memories.record_skirmish(skirmish)
        assert "Skirmish must involve the owner civilization." in str(
            context.exception)

    def test_record_skirmish_accepts_resolved_with_owner(self):
        """Verify that a valid resolved skirmish is recorded successfully."""
        skirmish = self._resolved_skirmish(self.owner, self.opponent)
        self.memories.record_skirmish(skirmish)

        history = self.memories.get_skirmish_history()
        assert len(history) == 1
        assert history[0] is skirmish

    def test_get_skirmish_history_filters_by_opponent(self):
        """Verify that skirmish history is filtered by opponent when specified."""
        s1 = self._resolved_skirmish(self.owner, self.opponent)
        s2 = self._resolved_skirmish(self.owner, self.other)
        self.memories.record_skirmish(s1)
        self.memories.record_skirmish(s2)

        filtered = self.memories.get_skirmish_history(opponent=self.opponent)
        assert filtered == [s1]

    def test_get_skirmish_history_last_n(self):
        """Verify that the last n skirmishes are returned correctly."""
        s1 = self._resolved_skirmish(self.owner, self.opponent)
        s2 = self._resolved_skirmish(self.owner, self.other)
        s3 = self._resolved_skirmish(self.owner, self.other_2)
        self.memories.record_skirmish(s1)
        self.memories.record_skirmish(s2)
        self.memories.record_skirmish(s3)

        tail = self.memories.get_skirmish_history(last_n=2)
        assert tail == [s2, s3]

    def test_get_skirmish_history_last_n_zero(self):
        """Verify that last_n=0 returns an empty list."""
        self.memories.record_skirmish(self._resolved_skirmish(
            self.owner, self.opponent))
        assert self.memories.get_skirmish_history(last_n=0) == []

    def test_get_skirmish_history_last_n_negative_raises(self):
        """Verify that negative last_n values raise validation error."""
        with self.assertRaises(MemoriesValidationExcept):
            self.memories.get_skirmish_history(last_n=-1)

    def test_get_skirmish_history_last_n_above_limit_raises(self):
        """Verify that last_n values above the limit raise validation error."""
        with self.assertRaises(MemoriesValidationExcept):
            self.memories.get_skirmish_history(last_n=1001)

    def test_get_skirmish_history_returns_copy(self):
        """Verify that skirmish history returns a copy, not the internal list."""
        s1 = self._resolved_skirmish(self.owner, self.opponent)
        self.memories.record_skirmish(s1)

        first = self.memories.get_skirmish_history()
        first.append(self._resolved_skirmish(self.owner, self.other))

        second = self.memories.get_skirmish_history()
        assert second == [s1]
