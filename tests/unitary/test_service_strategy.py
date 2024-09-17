import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.core.domain.models import Cost, Position
from app.core.domain.services import StrategyService
from app.infraestructure.exceptions.strategies import (
    NotSignedStrategyError, InvalidStrategyResponeError)


class TestStrategyService(TestCase):
    @patch('app.core.domain.services.strategies.uuid4')
    def setUp(self, mock_uuid4: MagicMock):
        self.mock_uuid4 = mock_uuid4
        self.strategy = MagicMock(
            return_value=True,
            __name__="test01",
            __signature__=hash(mock_uuid4.return_value)
        )
        self.civ1 = MagicMock(name="Self")
        self.civ2 = MagicMock(name="TestOpponent")
        self.planet = MagicMock(name="TestPlanet", cost=Cost.HIGH)
        self.proxy_factory = MagicMock(side_effect=lambda x: x)
        self.repository = MagicMock()
        self.service = StrategyService(
            repository=self.repository, proxy_factory=self.proxy_factory)

    def test_instance_success(self):
        assert self.repository == self.service.repository
        assert self.proxy_factory == self.service.proxy_factory
        assert (
            hash(self.mock_uuid4.return_value)
            == self.service._StrategyService__signature
        )

    def test_instance_mangle_property_failure(self):
        with self.assertRaises(AttributeError) as context:
            self.service.__signature
        assert (
            "'StrategyService' object has no attribute "
            "'_TestStrategyService__signature'"
            == str(context.exception)
        )

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
        assert self.proxy_factory.call_args_list == [
            call(self.civ2),
            call(self.planet),
            call(self.civ1.memory),
        ]

    @patch('logging.Logger.error')
    def test_mask_strategy_not_return_expected(
        self, mock_logger_error: MagicMock
    ):
        self.strategy.return_value = None
        masked_strategy = self.service.mask_strategy(self.strategy)
        assert Position.FAIL == masked_strategy(
            self.civ1, self.planet, self.civ2)
        self.strategy.assert_called_once_with(
            opponent=self.civ2,
            planet=self.planet,
            memories=self.civ1.memory,
            resources=self.civ1.resources,
        )
        assert (
            mock_logger_error.call_args and mock_logger_error.call_args[0]
            and isinstance(
                mock_logger_error.call_args[0][0], InvalidStrategyResponeError)
            and str(mock_logger_error.call_args[0][0]) == (
                "Strategy 'test01' must return a boolean value, got None")
        )
        assert self.proxy_factory.call_args_list == [
            call(self.civ2),
            call(self.planet),
            call(self.civ1.memory),
        ]

    @patch('logging.Logger.error')
    def test_mask_strategy_raise_exception_inside(
        self, mock_logger_error: MagicMock
    ):
        self.strategy.side_effect = AttributeError("simulated exception error")
        masked_strategy = self.service.mask_strategy(self.strategy)
        assert Position.FAIL == masked_strategy(
            self.civ1, self.planet, self.civ2)
        self.strategy.assert_called_once_with(
            opponent=self.civ2,
            planet=self.planet,
            memories=self.civ1.memory,
            resources=self.civ1.resources,
        )
        assert (
            mock_logger_error.call_args and mock_logger_error.call_args[0]
            and isinstance(mock_logger_error.call_args[0][0], Exception)
            and str(mock_logger_error.call_args[0][0]) == (
                "simulated exception error")
        )
        assert self.proxy_factory.call_args_list == [
            call(self.civ2),
            call(self.planet),
            call(self.civ1.memory),
        ]

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

    @patch('logging.Logger.critical')
    def test_validate_strategy_success(
        self,
        mock_logger_critical: MagicMock,
    ):
        assert self.service.validate_strategy(
            self.strategy, self.planet, self.civ1, self.civ2
        ) is True
        self.strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        mock_logger_critical.assert_not_called()

    @patch('logging.Logger.critical')
    def test_validate_strategy_response_failure(
        self,
        mock_logger_critical: MagicMock,
    ):
        self.strategy.return_value = None
        self.strategy.name = "test01"
        assert self.service.validate_strategy(
            self.strategy, self.planet, self.civ1, self.civ2
        ) is False
        self.strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        mock_logger_critical.assert_not_called()

    @patch('logging.Logger.critical')
    def test_validate_strategy_critical_failure(
        self,
        mock_logger_critical: MagicMock,
    ):
        self.strategy.side_effect = TypeError("simulated argument error")
        assert self.service.validate_strategy(
            self.strategy, self.planet, self.civ1, self.civ2
        ) is False
        self.strategy.assert_called_once_with(
            self=self.civ1,
            planet=self.planet,
            opponent=self.civ2,
        )
        assert mock_logger_critical.call_args_list == [
            call(self.strategy.side_effect, exc_info=False),
        ]

    @patch('logging.Logger.critical')
    def test_validate_strategy_critical_signature_failure(
        self,
        mock_logger_critical: MagicMock,
    ):
        self.strategy.__signature__ = "FAILEDSIGNATURE"
        self.strategy.name = "test01"
        assert self.service.validate_strategy(
            self.strategy, self.planet, self.civ1, self.civ2
        ) is False
        self.strategy.assert_not_called()
        assert (
            mock_logger_critical.call_args
            and mock_logger_critical.call_args[0]
            and isinstance(
                mock_logger_critical.call_args[0][0], NotSignedStrategyError)
            and "Invalid strategy signature of 'test01'"
                == str(mock_logger_critical.call_args[0][0])
        )
