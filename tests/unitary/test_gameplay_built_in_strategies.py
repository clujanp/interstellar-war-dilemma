import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from gameplay.classes import Civilization, Memories, Position
from gameplay.strategy import BuiltInStrategies


class TestBuiltInStrategies(TestCase):
    def setUp(self):
        self.mock_opponent = MagicMock(spec=Civilization)
        self.mock_memories = MagicMock(spec=Memories)

    def test_always_cooperation_success(self):
        result = BuiltInStrategies.always_cooperation()
        assert result == Position.COOPERATION

    def test_always_aggression_success(self):
        result = BuiltInStrategies.always_aggression()
        assert result == Position.AGGRESSION

    def test_random_success(self):
        result = BuiltInStrategies.random()
        assert result in [Position.COOPERATION, Position.AGGRESSION]

    def test_tic_for_tac_with_last_positions_success(self):
        self.mock_memories.last_positions.return_value = [Position.AGGRESSION]
        result = BuiltInStrategies.tic_for_tac(
            self.mock_opponent, self.mock_memories)
        assert result == Position.AGGRESSION
        self.mock_memories.last_positions.assert_called_once_with(
            self.mock_opponent)

    def test_tic_for_tac_without_last_positions_success(self):
        self.mock_memories.last_positions.return_value = []
        result = BuiltInStrategies.tic_for_tac(
            self.mock_opponent, self.mock_memories)
        assert result in [Position.COOPERATION, Position.AGGRESSION]
        self.mock_memories.last_positions.assert_called_once_with(
            self.mock_opponent)

    def test_friedman_with_aggressions_success(self):
        self.mock_memories.aggressions.return_value.percent = 0.5
        result = BuiltInStrategies.friedman(
            self.mock_opponent, self.mock_memories)
        assert result == Position.AGGRESSION
        self.mock_memories.aggressions.assert_called_once_with(
            self.mock_opponent)

    def test_friedman_without_aggressions_success(self):
        self.mock_memories.aggressions.return_value.percent = 0
        result = BuiltInStrategies.friedman(
            self.mock_opponent, self.mock_memories)
        assert result == Position.COOPERATION
        self.mock_memories.aggressions.assert_called_once_with(
            self.mock_opponent)

    @patch('gameplay.strategy.random')
    def test_joss_with_last_positions_success(self, mock_random: MagicMock):
        mock_random.return_value = 0.90
        self.mock_memories.last_positions.return_value = [Position.COOPERATION]
        result = BuiltInStrategies.joss(self.mock_opponent, self.mock_memories)
        assert result == self.mock_memories.last_positions.return_value[0]
        mock_random.assert_called_once_with()
        self.mock_memories.last_positions.assert_called_once_with(
            self.mock_opponent)

    @patch('gameplay.strategy.random')
    def test_joss_without_last_positions_taken_default_success(
        self, mock_random: MagicMock
    ):
        mock_random.return_value = 0.90
        self.mock_memories.last_positions.return_value = []
        result = BuiltInStrategies.joss(self.mock_opponent, self.mock_memories)
        assert result == Position.COOPERATION
        mock_random.assert_called_once_with()
        self.mock_memories.last_positions.assert_called_once_with(
            self.mock_opponent)

    @patch('gameplay.strategy.random')
    def test_joss_with_random_10_percent_success(self, mock_random: MagicMock):
        mock_random.return_value = 0.09
        self.mock_memories.last_positions.return_value = [Position.COOPERATION]
        result = BuiltInStrategies.joss(self.mock_opponent, self.mock_memories)
        assert result == Position.AGGRESSION
        mock_random.assert_called_once_with()
        self.mock_memories.last_positions.assert_not_called()

    def test_tester_first_skirmishes_success(self):
        self.mock_memories.skirmishes_count.return_value = 0
        result = BuiltInStrategies.tester(
            self.mock_opponent, self.mock_memories)
        assert Position.COOPERATION == result
        self.mock_memories.skirmishes_count.assert_called_once_with(
            self.mock_opponent)
        self.mock_memories.first_positions.assert_not_called()
        self.mock_memories.last_positions.assert_not_called()

    def test_tester_second_skirmishes_success(self):
        self.mock_memories.skirmishes_count.return_value = 1
        result = BuiltInStrategies.tester(
            self.mock_opponent, self.mock_memories)
        assert Position.AGGRESSION == result
        self.mock_memories.skirmishes_count.assert_called_once_with(
            self.mock_opponent)
        self.mock_memories.first_positions.assert_not_called()
        self.mock_memories.last_positions.assert_not_called()

    def test_tester_more_second_skirmish_with_second_aggression_success(self):
        self.mock_memories.skirmishes_count.return_value = 2
        self.mock_memories.first_positions.return_value = [
            Position.COOPERATION, Position.AGGRESSION]
        self.mock_memories.last_positions.return_value = [Position.AGGRESSION]
        result = BuiltInStrategies.tester(
            self.mock_opponent, self.mock_memories)
        assert Position.AGGRESSION == result
        self.mock_memories.skirmishes_count.assert_called_once_with(
            self.mock_opponent)
        self.mock_memories.first_positions.assert_called_once_with(
            self.mock_opponent, 2)
        self.mock_memories.last_positions.assert_called_once_with(
            self.mock_opponent)

    def test_tester_second_aggression_reply_last_success(self):
        self.mock_memories.skirmishes_count.return_value = 3
        self.mock_memories.first_positions.return_value = [
            Position.COOPERATION, Position.AGGRESSION, Position.COOPERATION]
        self.mock_memories.last_positions.return_value = [Position.COOPERATION]
        result = BuiltInStrategies.tester(
            self.mock_opponent, self.mock_memories)
        assert Position.COOPERATION == result
        self.mock_memories.skirmishes_count.assert_called_once_with(
            self.mock_opponent)
        self.mock_memories.first_positions.assert_called_once_with(
            self.mock_opponent, 2)
        self.mock_memories.last_positions.assert_called_once_with(
            self.mock_opponent)

    def test_tester_second_cooperation_expected_cooperation_success(self):
        self.mock_memories.skirmishes_count.return_value = 3
        self.mock_memories.first_positions.return_value = [
            Position.COOPERATION, Position.COOPERATION, Position.AGGRESSION]
        self.mock_memories.last_positions.return_value = [Position.COOPERATION]
        result = BuiltInStrategies.tester(
            self.mock_opponent, self.mock_memories)
        assert Position.COOPERATION == result
        self.mock_memories.skirmishes_count.assert_called_once_with(
            self.mock_opponent)
        self.mock_memories.first_positions.assert_called_once_with(
            self.mock_opponent, 2)
        self.mock_memories.last_positions.assert_not_called()

    def test_tester_second_cooperation_expected_aggression_success(self):
        self.mock_memories.skirmishes_count.return_value = 4
        self.mock_memories.first_positions.return_value = [
            Position.COOPERATION, Position.COOPERATION, Position.AGGRESSION,
            Position.COOPERATION
        ]
        self.mock_memories.last_positions.return_value = [Position.COOPERATION]
        result = BuiltInStrategies.tester(
            self.mock_opponent, self.mock_memories)
        assert Position.AGGRESSION == result
        self.mock_memories.skirmishes_count.assert_called_once_with(
            self.mock_opponent)
        self.mock_memories.first_positions.assert_called_once_with(
            self.mock_opponent, 2)
        self.mock_memories.last_positions.assert_not_called()
