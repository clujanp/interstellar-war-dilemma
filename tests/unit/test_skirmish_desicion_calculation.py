from unittest import TestCase
from app.core.domain.value_objects import SkirmishDecision as SD


class TestSkirmishDesicionCalculation(TestCase):
    """Test decision as enum calculation."""

    def setUp(self):
        """Set up cases."""

    def test_skirmish_decision_values(self):
        """Test the integer values of skirmish decisions."""
        assert SD.COOPERATE == 1
        assert SD.ATTACK == 2
        assert SD.NONE == 0
        assert len(SD) == 3

    def test_skirmish_operation(self):
        """Test math operations to solve skirmish based on decisions.
        `combined = first * N + second`"""

        assert SD.COOPERATE * len(SD) + SD.ATTACK == 5
        assert SD.ATTACK * len(SD) + SD.COOPERATE == 7
        assert SD.NONE * len(SD) + SD.COOPERATE == 1
        assert SD.COOPERATE * len(SD) + SD.COOPERATE == 4
        assert SD.NONE * len(SD) + SD.NONE == 0

    def test_reverse_skirmish_operation(self):
        """Test reverse math operations to solve skirmish.
        `first, second = divmod(combined, N)`"""
        assert divmod(5, len(SD)) == (SD.COOPERATE, SD.ATTACK,)
        assert divmod(7, len(SD)) == (SD.ATTACK,  SD.COOPERATE,)
        assert divmod(1, len(SD)) == (SD.NONE, SD.COOPERATE,)
        assert divmod(4, len(SD)) == (SD.COOPERATE, SD.COOPERATE,)
        assert divmod(0, len(SD)) == (SD.NONE, SD.NONE,)
