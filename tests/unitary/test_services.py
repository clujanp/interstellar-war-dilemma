import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, ANY
from app.core.domain.models import (
    Civilization, Planet, Score, Position, Eval)
from app.core.domain.services import (
    PlanetService, CivilizationService, SkirmishService, MemoriesService)


class TestPlanetService(TestCase):
    @patch(
        'app.core.domain.services.planet.planet_namer',
        return_value="TestPlanet"
    )
    def test_create_planet_with_default_values(
        self, mock_planet_namer: MagicMock
    ):
        planet = PlanetService.create()

        mock_planet_namer.assert_called_once()
        assert planet.name == "TestPlanet"
        assert planet.cost in PlanetService.COSTS

    @patch('app.utils.functions.planet_namer')
    def test_create_planet_with_custom_values(
        self, mock_planet_namer: MagicMock
    ):
        planet = PlanetService.create(
            name="CustomPlanet",
            cost=Score.COST_HIGH
        )
        mock_planet_namer.assert_not_called()
        assert planet.name == "CustomPlanet"
        assert planet.cost == Score.COST_HIGH


class TestCivilizationService(TestCase):
    def setUp(self):
        self.strategy = MagicMock(return_value=True)

    def test_create_civilization_success(self):
        civilization = CivilizationService.create(
            name="TestCiv",
            strategy=self.strategy,
            resources=10
        )
        assert civilization.name == "TestCiv"
        assert civilization.resources == 10
        assert civilization.memory.owner == civilization

    @patch('logging.Logger.error')
    @patch('app.core.domain.services.planet.PlanetService.create')
    @patch('app.core.domain.services.civilization.Civilization', autospec=True)
    def test_validate_strategy_success(
        self,
        mock_civilization: MagicMock,
        mock_planet_create: MagicMock,
        mock_logger_error: MagicMock,
    ):
        assert CivilizationService.validate_strategy(self.strategy) is True
        mock_planet_create.assert_called_once_with(
            name="TestPlanet", cost=Score.COST_HIGH)
        mock_civilization.assert_called_once_with(
            name="TestOpponent", strategy=ANY, resources=0)
        self.strategy.assert_called_once_with(
            planet=mock_planet_create.return_value,
            opponent=mock_civilization.return_value
        )
        mock_logger_error.assert_not_called()

    @patch('logging.Logger.error')
    @patch('app.core.domain.services.planet.PlanetService.create')
    @patch('app.core.domain.services.civilization.Civilization', autospec=True)
    def test_validate_strategy_type_error_failure(
        self,
        mock_civilization: MagicMock,
        mock_planet_create: MagicMock,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(
            side_effect=TypeError("simulated argument error"))
        assert CivilizationService.validate_strategy(mock_strategy) is False
        mock_planet_create.assert_called_once_with(
            name="TestPlanet", cost=Score.COST_HIGH)
        mock_civilization.assert_called_once_with(
            name="TestOpponent", strategy=ANY, resources=0)
        mock_strategy.assert_called_once_with(
            planet=mock_planet_create.return_value,
            opponent=mock_civilization.return_value
        )
        mock_logger_error.assert_called_with(mock_strategy.side_effect)

    @patch('logging.Logger.error')
    @patch('app.core.domain.services.planet.PlanetService.create')
    @patch('app.core.domain.services.civilization.Civilization', autospec=True)
    def test_validate_strategy_exception_failure(
        self,
        mock_civilization: MagicMock,
        mock_planet_create: MagicMock,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(
            side_effect=Exception("simulated exception error"))
        assert CivilizationService.validate_strategy(mock_strategy) is False
        mock_planet_create.assert_called_once_with(
            name="TestPlanet", cost=Score.COST_HIGH)
        mock_civilization.assert_called_once_with(
            name="TestOpponent", strategy=ANY, resources=0)
        mock_strategy.assert_called_once_with(
            planet=mock_planet_create.return_value,
            opponent=mock_civilization.return_value
        )
        mock_logger_error.assert_called_with(
            mock_strategy.side_effect, exc_info=True)

    @patch('app.core.domain.models.Memories.add')
    def test_remember_success(self, mock_memories_add):
        civilization = Civilization(
            name="TestCiv",
            strategy=self.strategy,
            resources=10
        )
        skirmish = MagicMock()
        CivilizationService.remember(civilization, skirmish)
        mock_memories_add.assert_called_once_with(skirmish)


class TestSkirmishService(TestCase):
    def setUp(self):
        self.planet = Planet(
            name="CustomPlanet",
            cost=Score.COST_HIGH
        )
        self.civilization_1 = Civilization(
            name="TestCiv1",
            strategy=MagicMock(return_value=True),
            resources=10
        )
        self.civilization_2 = Civilization(
            name="TestCiv2",
            strategy=MagicMock(return_value=False),
            resources=10,
        )

    def test_create_skirmish_success(self):
        skirmish = SkirmishService.create(
            self.planet,
            self.civilization_1,
            self.civilization_2
        )
        assert skirmish.planet == self.planet
        assert skirmish.civilization_1 == self.civilization_1
        assert skirmish.civilization_2 == self.civilization_2

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_already_resolved_success(
        self, mock_decide_winner
    ):
        skirmish = MagicMock(winner_=True)
        with self.assertRaises(ValueError) as context:
            SkirmishService.resolve(skirmish)
        assert "Skirmish already resolved" == str(context.exception)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_tie_good_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.COOPERATION
        skirmish.civilization_2.strategy.return_value = Position.COOPERATION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            [self.civilization_1, self.civilization_2], score_1, score_2)
        result = SkirmishService.resolve(skirmish)

        skirmish.civilization_1.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_2)
        skirmish.civilization_2.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_1)
        mock_decide_winner.assert_called_once_with(
            skirmish, Score.TIE_GOOD, Score.TIE_GOOD)
        assert result == (
            [self.civilization_1, self.civilization_2], score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_tie_bad_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.AGGRESSION
        skirmish.civilization_2.strategy.return_value = Position.AGGRESSION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            [self.civilization_1, self.civilization_2], score_1, score_2)
        result = SkirmishService.resolve(skirmish)

        skirmish.civilization_1.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_2)
        skirmish.civilization_2.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_1)
        mock_decide_winner.assert_called_once_with(
            skirmish, Score.TIE_BAD, Score.TIE_BAD)
        assert result == (
            [self.civilization_1, self.civilization_2], score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_first_win_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.AGGRESSION
        skirmish.civilization_2.strategy.return_value = Position.COOPERATION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            [self.civilization_1, self.civilization_2], score_1, score_2)
        result = SkirmishService.resolve(skirmish)

        skirmish.civilization_1.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_2)
        skirmish.civilization_2.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_1)
        mock_decide_winner.assert_called_once_with(
            skirmish, Score.WIN, Score.LOSE)
        assert result == (
            [self.civilization_1, self.civilization_2], score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_second_win_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.COOPERATION
        skirmish.civilization_2.strategy.return_value = Position.AGGRESSION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            [self.civilization_1, self.civilization_2], score_1, score_2)
        result = SkirmishService.resolve(skirmish)

        skirmish.civilization_1.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_2)
        skirmish.civilization_2.strategy.assert_called_once_with(
            planet=skirmish.planet, opponent=skirmish.civilization_1)
        mock_decide_winner.assert_called_once_with(
            skirmish, Score.LOSE, Score.WIN)
        assert result == (
            [self.civilization_1, self.civilization_2], score_1, score_2)

    def test_decide_winner_tie_good_success(self):
        skirmish = MagicMock()
        result = SkirmishService._decide_winner(
            skirmish, Score.TIE_GOOD, Score.TIE_GOOD)
        assert result == (
            [skirmish.civilization_1, skirmish.civilization_2],
            Score.TIE_GOOD,
            Score.TIE_GOOD
        )
        assert skirmish.score_1 == Score.TIE_GOOD
        assert skirmish.score_2 == Score.TIE_GOOD
        assert skirmish.winner_ == [
            skirmish.civilization_1, skirmish.civilization_2]
        assert skirmish.planet.colonizer == [
            skirmish.civilization_1, skirmish.civilization_2]

    def test_decide_winner_tie_bad_success(self):
        skirmish = MagicMock()
        result = SkirmishService._decide_winner(
            skirmish, Score.TIE_BAD, Score.TIE_BAD)
        assert result == (
            [skirmish.civilization_1, skirmish.civilization_2],
            Score.TIE_BAD,
            Score.TIE_BAD
        )
        assert skirmish.score_1 == Score.TIE_BAD
        assert skirmish.score_2 == Score.TIE_BAD
        assert skirmish.winner_ == [
            skirmish.civilization_1, skirmish.civilization_2]
        assert skirmish.planet.colonizer == [
            skirmish.civilization_1, skirmish.civilization_2]

    def test_decide_winner_first_win_success(self):
        skirmish = MagicMock()
        result = SkirmishService._decide_winner(
            skirmish, Score.WIN, Score.LOSE)
        assert result == (
            [skirmish.civilization_1],
            Score.WIN,
            Score.LOSE
        )
        assert skirmish.score_1 == Score.WIN
        assert skirmish.score_2 == Score.LOSE
        assert skirmish.winner_ == [skirmish.civilization_1]
        assert skirmish.planet.colonizer == [skirmish.civilization_1]

    def test_decide_winner_second_win_success(self):
        skirmish = MagicMock()
        result = SkirmishService._decide_winner(
            skirmish, Score.LOSE, Score.WIN)
        assert result == (
            [skirmish.civilization_2],
            Score.LOSE,
            Score.WIN
        )
        assert skirmish.score_1 == Score.LOSE
        assert skirmish.score_2 == Score.WIN
        assert skirmish.winner_ == [skirmish.civilization_2]
        assert skirmish.planet.colonizer == [skirmish.civilization_2]


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
        self.memories = MagicMock(owner=None)
        self.memories.civilizations.return_value = []
        self.memories.skirmishes.return_value = self.skirmishes
        self.memories.memories_ = [1, 2]

    def test_civilizations_success(self):
        assert MemoriesService.civilizations(self.memories) == []
        self.memories.civilizations.assert_called_once()

    @patch('app.core.domain.services.memories.Statistic')
    def test_statistics(self, mock_statiscs: MagicMock):
        response = MemoriesService._statistics(
            self.memories, self.civilization_1, self.rule)
        mock_statiscs.assert_called_once_with(
            1, total=len(self.memories.memories_))
        assert mock_statiscs.return_value == response

    @patch('app.core.domain.services.memories.MemoriesService._statistics')
    def test_cooperations(self, mock_statiscs_method: MagicMock):
        response = MemoriesService.cooperations(
            self.memories, self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.memories, self.civilization_1, Eval.was_cooperative)
        assert mock_statiscs_method.return_value == response

    @patch('app.core.domain.services.memories.MemoriesService.cooperations')
    def test_aggressions(self, mock_cooperations_method: MagicMock):
        response = MemoriesService.aggressions(
            self.memories, self.civilization_1)
        mock_cooperations_method.assert_called_once_with(
            self.memories, self.civilization_1)
        assert (
            mock_cooperations_method.return_value.invert.return_value
            == response
        )

    @patch('app.core.domain.services.memories.MemoriesService._statistics')
    def test_conquests(self, mock_statiscs_method: MagicMock):
        response = MemoriesService.conquests(
            self.memories, self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.memories, self.civilization_1, Eval.is_conquest)
        assert mock_statiscs_method.return_value == response

    @patch('app.core.domain.services.memories.MemoriesService._statistics')
    def test_hits(self, mock_statiscs_method: MagicMock):
        response = MemoriesService.hits(
            self.memories, self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.memories, self.civilization_1, Eval.is_hit)
        assert mock_statiscs_method.return_value == response

    @patch('app.core.domain.services.memories.MemoriesService._statistics')
    def test_mistakes(self, mock_statiscs_method: MagicMock):
        response = MemoriesService.mistakes(
            self.memories, self.civilization_1)
        mock_statiscs_method.assert_called_once_with(
            self.memories, self.civilization_1, Eval.is_mistake)
        assert mock_statiscs_method.return_value == response
