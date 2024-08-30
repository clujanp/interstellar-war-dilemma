import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.core.domain.models import Cost
from app.core.domain.services import StrategyService
from app.config.messages.en import ERR_STRATEGY_SERVICE


class TestStrategyService(TestCase):
    def setUp(self):
        self.strategy = MagicMock(return_value=True, __name__="test01")
        self.civ1 = MagicMock(name="Self")
        self.civ2 = MagicMock(name="TestOpponent")
        self.planet = MagicMock(name="TestPlanet", cost=Cost.HIGH)
        self.service = StrategyService(
            repository=MagicMock(), proxy_factory=MagicMock())

    def test_load_strategies(self):
        self.service.repository.load_strategies.return_value = {
            'test': self.strategy}
        assert self.service.load_strategies() == {'test': self.strategy}

    def test_mask_strategy(self):
        masked_strategy = self.service.mask_strategy(self.strategy)
        assert masked_strategy(self.civ1, self.planet, self.civ2) is True
        self.strategy.assert_called_once_with(
            opponent=self.civ2,
            planet=self.planet,
            memories=self.civ1.memory,
            resources=self.civ1.resources,
        )

    def test_mask_execution_entities(self):
        proxies = [MagicMock(), MagicMock(), MagicMock()]
        self.service.proxy_factory.side_effect = iter(proxies)
        assert self.service._mask_execution_entities(
            self.civ2, self.planet, MagicMock()) == (
            proxies[0],
            proxies[1],
            proxies[2],
        )

    def test_select_random_builtin(self):
        strategies = self.service.select_random_builtin()
        assert (
            strategies
            is self.service.repository.select_random_builtin.return_value
        )

    @patch('logging.Logger.error')
    def test_validate_strategy_success(
        self,
        mock_logger_error: MagicMock,
    ):
        assert self.service.validate_strategy(
            self.strategy, self.planet, self.civ1, self.civ2
        ) is True
        self.strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        mock_logger_error.assert_not_called()

    @patch('logging.Logger.error')
    def test_validate_strategy_response_failure(
        self,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(return_value=None)
        mock_strategy.name = "test01"
        assert self.service.validate_strategy(
            mock_strategy, self.planet, self.civ1, self.civ2
        ) is False
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        assert str(mock_logger_error.call_args_list[0][0][0]) == (
            ERR_STRATEGY_SERVICE['must_return'].format('test01', None))

    @patch('logging.Logger.error')
    def test_validate_strategy_type_error_failure(
        self,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(
            side_effect=TypeError("simulated argument error"))
        assert self.service.validate_strategy(
            mock_strategy, self.planet, self.civ1, self.civ2
        ) is False
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        assert mock_logger_error.call_args_list == [
            call(mock_strategy.side_effect, exc_info=False),
        ]

    @patch('logging.Logger.error')
    def test_validate_strategy_exception_failure(
        self,
        mock_logger_error: MagicMock,
    ):
        mock_strategy = MagicMock(
            side_effect=Exception("simulated exception error"))

        assert self.service.validate_strategy(
            mock_strategy, self.planet, self.civ1, self.civ2
        ) is False
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        assert mock_logger_error.call_args_list == [
            call(mock_strategy.side_effect, exc_info=False),
        ]
