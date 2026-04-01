from unittest import TestCase
from app.domain.models import Civilization, AstronomyBody, Skirmish
from app.domain.exceptions import SkirmishResolvedExcept
from app.domain.value_objects import (
    AstronomicObjectType as AstroType, Decision, Resources, Resolution)


class TestSkirmish(TestCase):
    def setUp(self):
        """Set up test data for skirmish tests."""
        self.siwenna = AstronomyBody(
            name="Siwenna", type=AstroType.PLANET, resources=Resources(10))
        self.fundation = Civilization(
            name="Foundation", home=self.siwenna)
        self.empire = Civilization(
            name="Empire", home=self.siwenna)
        self.skirmish = Skirmish(
            civ_a=self.fundation,
            civ_b=self.empire,
            astronomical_object=self.siwenna
        )

    def test_skirmish_defined(self):
        """Test instantiation of a skirmish."""
        assert self.skirmish.civ_a == self.fundation
        assert self.skirmish.civ_b == self.empire
        assert self.skirmish.astronomical_object == self.siwenna
        assert self.skirmish.resolution == Resolution.NOT_RESOLVED
        assert self.skirmish.decision_a is None
        assert self.skirmish.decision_b is None
        assert self.skirmish.civ_a_resources_gained == Resources.NONE
        assert self.skirmish.civ_b_resources_gained == Resources.NONE
        assert not self.skirmish.is_resolved
        
    def test_skirmish_same_civilization(self):
        """Test that a skirmish cannot be created with the same civilization."""
        with self.assertRaises(ValueError) as context:
            Skirmish(
                civ_a=self.fundation,
                civ_b=self.fundation,
                astronomical_object=self.siwenna
            )
        assert "Both civilizations in a skirmish must be different." in str(
            context.exception)

    def test_skirmish_resolve_cooperation(self):
        """Test skirmish when civilizations decide to cooperate."""
        self.skirmish.decision_a = Decision.COOPERATE
        self.skirmish.decision_b = Decision.COOPERATE
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.COOPERATION
        assert self.skirmish.civ_a_resources_gained == Resources(5)
        assert self.skirmish.civ_b_resources_gained == Resources(5)
        assert self.siwenna.owner == [self.fundation, self.empire]
        assert self.skirmish.is_resolved       
        
    def test_skirmish_resolve_betrayal_a(self):
        """Test skirmish when civ A defects and civ B cooperates."""
        self.skirmish.decision_a = Decision.DEFECT
        self.skirmish.decision_b = Decision.COOPERATE
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.BETRAYAL_A
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.BETRAYAL_A.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.BETRAYAL_A.value[1])
        assert self.siwenna.owner == [self.fundation]
        assert self.skirmish.is_resolved
        
    def test_skirmish_resolve_betrayal_b(self):
        """Test skirmish when civ A cooperates and civ B defects."""
        self.skirmish.decision_a = Decision.COOPERATE
        self.skirmish.decision_b = Decision.DEFECT
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.BETRAYAL_B
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.BETRAYAL_B.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.BETRAYAL_B.value[1])
        assert self.siwenna.owner == [self.empire]
        assert self.skirmish.is_resolved
        
    def test_skirmish_resolve_conflict(self):
        """Test skirmish when both civilizations defect."""
        self.skirmish.decision_a = Decision.DEFECT
        self.skirmish.decision_b = Decision.DEFECT
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.CONFLICT
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.CONFLICT.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.CONFLICT.value[1])
        assert self.siwenna.owner == [self.fundation, self.empire]
        assert self.skirmish.is_resolved

    def test_skirmish_resolve_not_responded(self):
        """Test matrix path when both civilizations do not respond."""
        self.skirmish.decision_a = Decision.NOT_DECIDED
        self.skirmish.decision_b = Decision.NOT_DECIDED
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.NOT_RESPONDED
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.NOT_RESPONDED.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.NOT_RESPONDED.value[1])
        assert self.siwenna.owner == [self.fundation, self.empire]
        assert self.skirmish.is_resolved
        
    def test_skirmish_resolve_not_cooperate_a(self):
        """Test matrix path when civ A does not respond and civ B cooperates."""
        self.skirmish.decision_a = Decision.NOT_DECIDED
        self.skirmish.decision_b = Decision.COOPERATE
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.NOT_COOPERATE_A
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.NOT_COOPERATE_A.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.NOT_COOPERATE_A.value[1])
        assert self.siwenna.owner == [self.empire]
        assert self.skirmish.is_resolved
        
    def test_skirmish_resolve_not_cooperate_b(self):
        """Test matrix path when civ A cooperates and civ B does not respond."""
        self.skirmish.decision_a = Decision.COOPERATE
        self.skirmish.decision_b = Decision.NOT_DECIDED
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.NOT_COOPERATE_B
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.NOT_COOPERATE_B.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.NOT_COOPERATE_B.value[1])
        assert self.siwenna.owner == [self.fundation]
        assert self.skirmish.is_resolved

    def test_skirmish_resolve_massacre_a(self):
        """Test matrix path when civ A does not respond and civ B defects."""
        self.skirmish.decision_a = Decision.NOT_DECIDED
        self.skirmish.decision_b = Decision.DEFECT
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.MASSACRE_A
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.MASSACRE_A.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.MASSACRE_A.value[1])
        assert self.siwenna.owner == [self.fundation]
        assert self.skirmish.is_resolved

    def test_skirmish_resolve_massacre_b(self):
        """Test matrix path when civ A defects and civ B does not respond."""
        self.skirmish.decision_a = Decision.DEFECT
        self.skirmish.decision_b = Decision.NOT_DECIDED
        self.skirmish.resolve()

        assert self.skirmish.resolution == Resolution.MASSACRE_B
        assert self.skirmish.civ_a_resources_gained == Resources(
            10 * Resolution.MASSACRE_B.value[0])
        assert self.skirmish.civ_b_resources_gained == Resources(
            10 * Resolution.MASSACRE_B.value[1])
        assert self.siwenna.owner == [self.empire]
        assert self.skirmish.is_resolved
        
    def test_skirmish_resolve_without_decisions(self):
        """Test that a skirmish cannot be resolved without decisions."""
        with self.assertRaises(Exception) as context:
            self.skirmish.resolve()
        assert (
            "Both civilizations must make a decision before "
            "resolving the skirmish."
        ) in str(context.exception)

    def test_skirmish_resolve_already_resolved(self):
        """Test that a skirmish cannot be resolved more than once."""
        self.skirmish.decision_a = Decision.COOPERATE
        self.skirmish.decision_b = Decision.COOPERATE
        self.skirmish.resolve()

        with self.assertRaises(Exception) as context:
            self.skirmish.resolve()
        assert "Skirmish has already been resolved." in str(context.exception)

    def test_skirmish_allows_changes_before_resolution(self):
        """Test that skirmish can be mutated before being resolved."""
        self.skirmish.decision_a = Decision.COOPERATE
        self.skirmish.decision_b = Decision.DEFECT

        assert self.skirmish.decision_a == Decision.COOPERATE
        assert self.skirmish.decision_b == Decision.DEFECT

    def test_skirmish_frozen_after_resolution(self):
        """Test that skirmish cannot be modified after it is resolved."""
        self.skirmish.decision_a = Decision.COOPERATE
        self.skirmish.decision_b = Decision.COOPERATE
        self.skirmish.resolve()

        with self.assertRaises(SkirmishResolvedExcept) as context:
            self.skirmish.decision_a = Decision.DEFECT
        assert "Skirmish is frozen after resolution." in str(context.exception)
        assert self.skirmish.is_resolved