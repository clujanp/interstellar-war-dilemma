import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.core.domain.models import Score, Position, Result
from app.core.domain.services import MemoriesServiceWrapper


class TestModelMemories(TestCase):
    def setUp(self):
        self.civilization_1 = MagicMock()
        self.civilization_2 = MagicMock()
        self.civilization_3 = MagicMock()
        self.rule = MagicMock(return_value=True)
        self.skirmishes = {
            self.civilization_1: [(Position.COOPERATION, Score.LOSE,)],
            self.civilization_2: [(Position.AGGRESSION, Score.WIN,)],
        }
        self.memories = MagicMock(name='memories', owner=None)
        self.memories.skirmishes.return_value = self.skirmishes
        self.memories.memories_ = [1, 2]
        self.memory_wrapped = MemoriesServiceWrapper(self.memories)

    def test_instance_success(self):
        assert self.memory_wrapped._memories == self.memories

    @patch('app.core.domain.services.memories.Memories')
    def test_instance_default_success(self, mock_memories: MagicMock):
        memory_wrapped = MemoriesServiceWrapper()
        mock_memories.assert_called_once_with(owner=None)
        assert memory_wrapped._memories == mock_memories.return_value

    def test_remembers_success(self):
        skirmish = MagicMock()
        self.memory_wrapped.remember(skirmish)
        self.memories.add.assert_called_once_with(skirmish)

    def test_civilizations_success(self):
        assert (
            self.memory_wrapped.civilizations()
            == self.memories.civilizations
        )

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper'
        '.skirmishes_count'
    )
    @patch('app.core.domain.services.memories.Statistic')
    def test_statistics(
        self,
        mock_statiscs: MagicMock,
        mock_skirmishes_count: MagicMock
    ):
        self.memories.skirmishes_by_civilization.return_value = {
            self.civilization_1: [('posture', 'score')]}
        mock_skirmishes_count.return_value = 1
        response = self.memory_wrapped._statistics(
            self.civilization_1, self.rule)

        mock_statiscs.assert_called_once_with(1, total=1)
        assert mock_statiscs.return_value == response

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper._statistics'
    )
    def test_cooperations(self, mock_statiscs_method: MagicMock):
        response = self.memory_wrapped.cooperations(self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.civilization_1, Result.was_cooperative)
        assert mock_statiscs_method.return_value == response

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper.cooperations'
    )
    def test_aggressions(self, mock_cooperations_method: MagicMock):
        response = self.memory_wrapped.aggressions(self.civilization_1)
        mock_cooperations_method.assert_called_once_with(self.civilization_1)
        assert (
            mock_cooperations_method.return_value.invert.return_value
            == response
        )

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper._statistics'
    )
    def test_conquests(self, mock_statiscs_method: MagicMock):
        response = self.memory_wrapped.conquests(self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.civilization_1, Result.is_conquest)
        assert mock_statiscs_method.return_value == response

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper._statistics'
    )
    def test_hits(self, mock_statiscs_method: MagicMock):
        response = self.memory_wrapped.hits(self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.civilization_1, Result.is_hit)
        assert mock_statiscs_method.return_value == response

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper._statistics'
    )
    def test_mistakes(self, mock_statiscs_method: MagicMock):
        response = self.memory_wrapped.mistakes(self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.civilization_1, Result.is_mistake)
        assert mock_statiscs_method.return_value == response
