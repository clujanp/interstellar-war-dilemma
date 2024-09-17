import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.core.domain.models import Civilization, Planet, Cost, Position
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
        self.mock_resoluter = MagicMock()
        self.service = SkirmishService(resoluter=self.mock_resoluter)

    def test_create_skirmish_success(self):
        skirmish = self.service.create(
            self.planet,
            self.civilization_1,
            self.civilization_2
        )
        assert skirmish.planet == self.planet
        assert skirmish.civilization_1 == self.civilization_1
        assert skirmish.civilization_2 == self.civilization_2

    def test_results_success(self):
        skirmish = MagicMock()
        result = self.service.results(skirmish)
        assert result == (
            skirmish.winner_, skirmish.score_1, skirmish.score_2)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_already_resolved_fail(
        self, mock_decide_winner
    ):
        skirmish = MagicMock(winner_=True)
        with self.assertRaises(ValueError) as context:
            self.service.resolve(skirmish)
        assert "Skirmish already resolved" == str(context.exception)

    @patch('app.core.domain.services.skirmish.SkirmishService._decide_winner')
    def test_resolve_skirmish_tie_good_success(self, mock_decide_winner):
        skirmish = MagicMock(winner_=None)
        skirmish.civilization_1.strategy.return_value = Position.COOPERATION
        skirmish.civilization_2.strategy.return_value = Position.AGGRESSION
        score_1 = MagicMock()
        score_2 = MagicMock()
        result = MagicMock()
        mock_decide_winner.return_value = (
            (self.civilization_1, self.civilization_2,),
            score_1,
            score_2,
            result
        )
        result = self.service.resolve(skirmish)

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
            Position.COOPERATION,
            Position.AGGRESSION,
            skirmish.civilization_1,
            skirmish.civilization_2
        )
        assert mock_decide_winner.return_value == result

    def test_decide_winner_success(self):
        self.mock_resoluter.__getitem__.return_value.return_value = MagicMock()
        result = self.service._decide_winner(
            Position.AGGRESSION,
            Position.COOPERATION,
            self.civilization_1,
            self.civilization_2
        )
        assert (
            self.mock_resoluter.__getitem__.return_value.return_value
            == result
        )
        self.mock_resoluter.__getitem__.assert_called_once_with(
            (Position.AGGRESSION, Position.COOPERATION,))
        self.mock_resoluter.__getitem__.return_value\
            .assert_called_once_with(self.civilization_1, self.civilization_2)
