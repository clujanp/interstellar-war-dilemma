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
            (self.civilization_1, self.civilization_2,), score_1, score_2)
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
        mock_decide_winner.assert_called_once_with(skirmish)
        assert result == (
            (self.civilization_1, self.civilization_2,), score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_tie_bad_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.AGGRESSION
        skirmish.civilization_2.strategy.return_value = Position.AGGRESSION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            (self.civilization_1, self.civilization_2,), score_1, score_2)
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
        mock_decide_winner.assert_called_once_with(skirmish)
        assert result == (
            (self.civilization_1, self.civilization_2,), score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_first_win_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.AGGRESSION
        skirmish.civilization_2.strategy.return_value = Position.COOPERATION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            (self.civilization_1, self.civilization_2,), score_1, score_2)
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
        mock_decide_winner.assert_called_once_with(skirmish)
        assert result == (
            (self.civilization_1, self.civilization_2,), score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_second_win_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.COOPERATION
        skirmish.civilization_2.strategy.return_value = Position.AGGRESSION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            (self.civilization_1, self.civilization_2,), score_1, score_2)
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
        mock_decide_winner.assert_called_once_with(skirmish)
        assert result == (
            (self.civilization_1, self.civilization_2,), score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_fail_and_aggression_success(
        self, mock_decide_winner
    ):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.FAIL
        skirmish.civilization_2.strategy.return_value = Position.AGGRESSION
        score_1 = MagicMock()
        score_2 = MagicMock()
        mock_decide_winner.return_value = (
            (self.civilization_2,), score_1, score_2)
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
        mock_decide_winner.assert_called_once_with(skirmish)
        assert result == (
            (self.civilization_2,), score_1, score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService.RESOLUTER')
    def test_decide_winner_success(self, mock_choises: MagicMock):
        skirmish = MagicMock(posture_1='a', posture_2='b')
        mock_choises.get.return_value = MagicMock(
            return_value=(
                (skirmish.civilization_1, skirmish.civilization_2,),
                Score.TIE_GOOD,
                Score.TIE_GOOD,
            ))
        result = SkirmishService._decide_winner(skirmish)
        assert mock_choises.get.return_value.return_value == result
        mock_choises.get.assert_called_once_with(('a', 'b'))
        mock_choises.get.return_value.assert_called_once_with(
            skirmish.civilization_1, skirmish.civilization_2)
        assert skirmish.score_1 == Score.TIE_GOOD
        assert skirmish.score_2 == Score.TIE_GOOD
        assert skirmish.winner_ == (
            skirmish.civilization_1, skirmish.civilization_2,)
        assert skirmish.planet.colonizer == (
            skirmish.civilization_1, skirmish.civilization_2,)

    def test_resoluter_success(self):
        COO, AGR, FAIL = (
            Position.COOPERATION, Position.AGGRESSION, Position.FAIL)
        WIN, LOSE, TIE_GOOD, TIE_BAD, MAX = (
            Score.WIN, Score.LOSE, Score.TIE_GOOD, Score.TIE_BAD,
            Score.MAX_SCORE
        )
        resoluter = SkirmishService.RESOLUTER
        civ1, civ2 = self.civilization_1, self.civilization_2

        assert ((civ1, civ2,), TIE_GOOD, TIE_GOOD) == resoluter.get(
            (COO, COO,))(civ1, civ2)
        assert ((civ1, civ2,), TIE_BAD, TIE_BAD) == resoluter.get(
            (AGR, AGR,))(civ1, civ2)
        assert ((civ2,), LOSE, WIN) == resoluter.get(
            (COO, AGR,))(civ1, civ2)
        assert ((civ1,), WIN, LOSE) == resoluter.get(
            (AGR, COO,))(civ1, civ2)
        # fail cases
        assert ((civ2,), LOSE, TIE_GOOD) == resoluter.get(
            (FAIL, COO,))(civ1, civ2)
        assert ((civ1,), TIE_GOOD, LOSE) == resoluter.get(
            (COO, FAIL,))(civ1, civ2)
        assert ((civ2,), LOSE, MAX) == resoluter.get(
            (FAIL, AGR,))(civ1, civ2)
        assert ((civ1,), MAX, LOSE) == resoluter.get(
            (AGR, FAIL,))(civ1, civ2)
        assert (tuple(), LOSE, LOSE) == resoluter.get(
            (FAIL, FAIL,))(civ1, civ2)
