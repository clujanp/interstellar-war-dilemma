from unittest import TestCase
from app.core.domain.value_objects import Decision as D, SkirmishResult as SR


class TestSkirmishDesicionCalculation(TestCase):
    """Test decision as enum calculation."""

    def setUp(self):
        """Set up cases."""

    def operation(self, first: D, second: D) -> SR:
        """Placeholder for operation test."""
        return SR(first * len(D) + second)

    def reverse(self, combined: SR) -> tuple[D, D]:
        """Reverse the operation to get the original decisions."""
        first, second = divmod(combined, len(D))
        return D(first), D(second)

    def test_skirmish_decision_values(self):
        """Test the integer values of skirmish decisions."""
        assert D.COOPERATE == 1
        assert D.ATTACK == 2
        assert D.NONE == 0
        assert len(D) == 3

    def test_skirmish_operation(self):
        """Test math operations to solve skirmish based on decisions.
        `combined = first * N + second`"""

        assert self.operation(D.COOPERATE, D.COOPERATE) == SR.COOPERATION
        assert self.operation(D.ATTACK, D.COOPERATE) == SR.TREASON_A
        assert self.operation(D.COOPERATE, D.ATTACK) == SR.TREASON_B
        assert self.operation(D.ATTACK, D.ATTACK) == SR.CONFLICT
        assert self.operation(D.COOPERATE, D.NONE) == SR.ASSIMILATION_A
        assert self.operation(D.NONE, D.COOPERATE) == SR.ASSIMILATION_B
        assert self.operation(D.ATTACK, D.NONE) == SR.MASSACRE_A
        assert self.operation(D.NONE, D.ATTACK) == SR.MASSACRE_B
        assert self.operation(D.NONE, D.NONE) == SR.LOOSE

    def test_reverse_skirmish_operation(self):
        """Test reverse math operations to solve skirmish.
        `first, second = divmod(combined, N)`"""
        assert self.reverse(SR.COOPERATION) == (D.COOPERATE, D.COOPERATE,)
        assert self.reverse(SR.TREASON_A) == (D.ATTACK,  D.COOPERATE,)
        assert self.reverse(SR.TREASON_B) == (D.COOPERATE, D.ATTACK,)
        assert self.reverse(SR.CONFLICT) == (D.ATTACK, D.ATTACK,)
        assert self.reverse(SR.ASSIMILATION_A) == (D.COOPERATE, D.NONE,)
        assert self.reverse(SR.ASSIMILATION_B) == (D.NONE, D.COOPERATE,)
        assert self.reverse(SR.MASSACRE_A) == (D.ATTACK, D.NONE,)
        assert self.reverse(SR.MASSACRE_B) == (D.NONE, D.ATTACK,)
        assert self.reverse(SR.LOOSE) == (D.NONE, D.NONE,)
