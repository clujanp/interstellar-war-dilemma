import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.core.domain.models import Cost
from app.core.domain.services import StrategyService


class TestStrategyService(TestCase):
    def setUp(self):
        self.strategy = MagicMock(return_value=True)
        self.civ1 = MagicMock(name="Self")
        self.civ2 = MagicMock(name="TestOpponent")
        self.planet = MagicMock(name="TestPlanet", cost=Cost.HIGH)

    @patch('logging.Logger.error')
    def test_validate_strategy_success(
        self,
        mock_logger_error: MagicMock,
    ):
        assert StrategyService.validate_strategy(
            self.strategy, self.planet, self.civ1, self.civ2
        ) is True
        self.strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        mock_logger_error.assert_not_called()

    @patch('logging.Logger.error')
    def test_validate_strategy_type_error_failure(
        self,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(
            side_effect=TypeError("simulated argument error"))
        assert StrategyService.validate_strategy(
            mock_strategy, self.planet, self.civ1, self.civ2
        ) is False
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        assert mock_logger_error.call_args_list == [
            call('-' * 80),
            call(mock_strategy.side_effect, exc_info=True),
            call('-' * 80),
        ]

    @patch('logging.Logger.error')
    def test_validate_strategy_exception_failure(
        self,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(
            side_effect=Exception("simulated exception error"))

        assert StrategyService.validate_strategy(
            mock_strategy, self.planet, self.civ1, self.civ2
        ) is False
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        assert mock_logger_error.call_args_list == [
            call('-' * 80),
            call(mock_strategy.side_effect, exc_info=True),
            call('-' * 80),
        ]
