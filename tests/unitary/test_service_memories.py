import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, PropertyMock
from app.core.domain.models import Score, Position, Result, Skirmish
from app.core.domain.services import MemoriesServiceWrapper


class TestModelMemories(TestCase):
    def setUp(self):
        self.civilization_1 = MagicMock()
        self.civilization_2 = MagicMock()
        self.civilization_3 = MagicMock()
        self.rule = MagicMock(return_value=True)
        self.planet_1 = MagicMock(cost=100)
        self.planet_2 = MagicMock(cost=200)
        self.skirmish_1 = MagicMock(spec=Skirmish, planet=self.planet_1)
        self.skirmish_2 = MagicMock(spec=Skirmish, planet=self.planet_2)
        self.skirmish_3 = MagicMock(spec=Skirmish, planet=self.planet_2)
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

    def test_owner_success(self):
        assert self.memory_wrapped.owner == self.memories.owner

    def test_length_success(self):
        assert self.memory_wrapped.length == 2

    def test_remembers_success(self):
        skirmish = MagicMock()
        self.memory_wrapped.remember(skirmish)
        self.memories.add.assert_called_once_with(skirmish)

    def test_civilizations_success(self):
        assert (
            self.memory_wrapped.civilizations()
            == self.memories.civilizations
        )

    def test_skirmishes_count_success(self):
        self.memories.skirmishes_count_by_civilization.return_value = {
            self.civilization_1: 1
        }
        assert (
            self.memory_wrapped.skirmishes_count(self.civilization_1) == 1)

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
    def test_loss(self, mock_statiscs_method: MagicMock):
        response = self.memory_wrapped.loss(self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.civilization_1, Result.is_lose)
        assert mock_statiscs_method.return_value == response

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper._statistics'
    )
    def test_mistakes(self, mock_statiscs_method: MagicMock):
        response = self.memory_wrapped.mistakes(self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.civilization_1, Result.is_mistake)
        assert mock_statiscs_method.return_value == response

    def test_score(self):
        self.memories.skirmishes_by_civilization.return_value = {
            self.civilization_1: [
                (Position.COOPERATION, Score.LOSE,),
                (Position.COOPERATION, Score.WIN,),
                (Position.COOPERATION, Score.TIE_GOOD,),
            ],
        }
        expected = sum([
            score for position, score in (
                self.memories.skirmishes_by_civilization.return_value[
                    self.civilization_1])
        ])
        response = self.memory_wrapped.score(self.civilization_1)
        assert expected == response

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper'
        '.civilizations'
    )
    @patch('app.core.domain.services.memories.MemoriesServiceWrapper.score')
    @patch('app.core.domain.services.memories.MemoriesServiceWrapper.hits')
    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper.cooperations'
    )
    def test_summary_success(
        self,
        mock_cooperations: MagicMock,
        mock_hits: MagicMock,
        mock_score: MagicMock,
        mock_civilizations: MagicMock,
    ):
        mock_civilizations.return_value = [
            self.civilization_1, self.civilization_2]
        mock_score.side_effect = [10, 5]
        mock_hits.side_effect = [MagicMock(percent=80), MagicMock(percent=60)]
        mock_cooperations.side_effect = [
            MagicMock(percent=70), MagicMock(percent=50)]

        response = self.memory_wrapped.summary()

        mock_score.assert_any_call(self.civilization_1)
        mock_score.assert_any_call(self.civilization_2)
        mock_hits.assert_any_call(self.civilization_1)
        mock_hits.assert_any_call(self.civilization_2)
        mock_cooperations.assert_any_call(self.civilization_1)
        mock_cooperations.assert_any_call(self.civilization_2)
        assert response == {
            self.civilization_1: {'score': 10, 'accuracy': 80, 'position': 70},
            self.civilization_2: {'score': 5, 'accuracy': 60, 'position': 50}
        }

    @patch(
        'app.core.domain.services.memories.MemoriesServiceWrapper.length',
        new_callable=PropertyMock
    )
    def test_report_success(self, mock_length: MagicMock):
        mock_length.return_value = 3
        self.memories.skirmishes = [
            self.skirmish_1, self.skirmish_2, self.skirmish_3]
        self.skirmish_1.result = Result.COOPERATION
        self.skirmish_2.result = Result.CONQUEST
        self.skirmish_3.result = Result.AGGRESSION
        self.skirmish_1.combined_score = 10
        self.skirmish_2.combined_score = 20
        self.skirmish_3.combined_score = 30

        response = self.memory_wrapped.report()

        assert response == {
            'skirmishes': 3,
            'max_score_reachable': Score.MAX_SCORE * 3,
            'score_reached': 60,
            'resolutions': {
                'cooperations': 1, 'conquests': 1, 'aggressions': 1},
            'avg_planets_cost': 500 / 3
        }
