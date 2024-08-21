import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.core.domain.models import Civilization, Planet, Score, Cost, Position
from app.core.domain.services import SkirmishService


class TestSkirmishService(TestCase):
    def setUp(self):
        self.planet = Planet(
            name="CustomPlanet",
            cost=Cost.HIGH
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

    def test_results_success(self):
        skirmish = MagicMock()
        result = SkirmishService.results(skirmish)
        assert result == (
            skirmish.winner_, skirmish.score_1, skirmish.score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_already_resolved_fail(
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
            self=skirmish.civilization_1,
            planet=skirmish.planet,
            opponent=skirmish.civilization_2
        )
        skirmish.civilization_2.strategy.assert_called_once_with(
            self=skirmish.civilization_2,
            planet=skirmish.planet,
            opponent=skirmish.civilization_1
        )
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
            self=skirmish.civilization_1,
            planet=skirmish.planet,
            opponent=skirmish.civilization_2
        )
        skirmish.civilization_2.strategy.assert_called_once_with(
            self=skirmish.civilization_2,
            planet=skirmish.planet,
            opponent=skirmish.civilization_1
        )
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
            self=skirmish.civilization_1,
            planet=skirmish.planet,
            opponent=skirmish.civilization_2
        )
        skirmish.civilization_2.strategy.assert_called_once_with(
            self=skirmish.civilization_2,
            planet=skirmish.planet,
            opponent=skirmish.civilization_1
        )
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
            self=skirmish.civilization_1,
            planet=skirmish.planet,
            opponent=skirmish.civilization_2
        )
        skirmish.civilization_2.strategy.assert_called_once_with(
            self=skirmish.civilization_2,
            planet=skirmish.planet,
            opponent=skirmish.civilization_1
        )
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
