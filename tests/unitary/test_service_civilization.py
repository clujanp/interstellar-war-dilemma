import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, ANY, call
from app.core.domain.models import Cost
from app.core.domain.services import CivilizationService


class TestCivilizationService(TestCase):
    def setUp(self):
        self.strategy = MagicMock(return_value=True)
        self.civ1 = MagicMock(name="Self")
        self.civ2 = MagicMock(name="TestOpponent")

    @patch('app.core.domain.models.models.Memories')
    @patch('app.core.domain.services.civilization.MemoriesServiceWrapper')
    @patch(
        'app.core.domain.services.civilization.CivilizationService'
        '.validate_strategy'
    )
    def test_create_civilization_success(
        self,
        mock_validate_strategy: MagicMock,
        mock_memories_wrapper: MagicMock,
        mock_memories: MagicMock,
    ):
        mock_validate_strategy.return_value = True
        civilization = CivilizationService.create(
            name="TestCiv",
            strategy=self.strategy,
            resources=10,
            skip_validation=False,
        )
        mock_validate_strategy.assert_called_once_with(self.strategy)
        mock_memories_wrapper.assert_called_once_with(
            mock_memories.return_value)
        assert civilization.name == "TestCiv"
        assert civilization.resources == 10
        assert (
            civilization.memory.owner
            == mock_memories_wrapper.return_value.owner
        )

    @patch('app.core.domain.models.models.Memories')
    @patch('app.core.domain.services.civilization.MemoriesServiceWrapper')
    @patch(
        'app.core.domain.services.civilization.CivilizationService'
        '.validate_strategy'
    )
    def test_create_civilization_skip_validateion_success(
        self,
        mock_validate_strategy: MagicMock,
        mock_memories_wrapper: MagicMock,
        mock_memories: MagicMock,
    ):
        civilization = CivilizationService.create(
            name="TestCiv",
            strategy=self.strategy,
            resources=10,
            skip_validation=True,
        )
        mock_validate_strategy.assert_not_called
        assert civilization.name == "TestCiv"
        assert civilization.resources == 10
        assert (
            civilization.memory.owner
            == mock_memories_wrapper.return_value.owner
        )

    @patch('logging.Logger.error')
    @patch('app.core.domain.services.planet.PlanetService.create')
    @patch('app.core.domain.services.civilization.Civilization', autospec=True)
    def test_validate_strategy_success(
        self,
        mock_civilization: MagicMock,
        mock_planet_create: MagicMock,
        mock_logger_error: MagicMock,
    ):
        mock_civilization.side_effect = [self.civ1, self.civ2]
        assert CivilizationService.validate_strategy(self.strategy) is True
        mock_planet_create.assert_called_once_with(
            name="TestPlanet", cost=Cost.HIGH)
        assert mock_civilization.call_args_list == [
            call(name="Self", strategy=ANY, resources=0),
            call(name="TestOpponent", strategy=ANY, resources=0),
        ]
        self.strategy.assert_called_once_with(
            self=self.civ1,
            planet=mock_planet_create.return_value,
            opponent=self.civ2,
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
        mock_civilization.side_effect = [self.civ1, self.civ2]
        mock_strategy = MagicMock(
            side_effect=TypeError("simulated argument error"))
        assert CivilizationService.validate_strategy(mock_strategy) is False
        mock_planet_create.assert_called_once_with(
            name="TestPlanet", cost=Cost.HIGH)
        assert mock_civilization.call_args_list == [
            call(name="Self", strategy=ANY, resources=0),
            call(name="TestOpponent", strategy=ANY, resources=0),
        ]
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=mock_planet_create.return_value,
            opponent=self.civ2,
        )
        assert mock_logger_error.call_args_list == [
            call('-' * 80),
            call(mock_strategy.side_effect, exc_info=True),
            call('-' * 80),
        ]

    @patch('logging.Logger.error')
    @patch('app.core.domain.services.planet.PlanetService.create')
    @patch('app.core.domain.services.civilization.Civilization', autospec=True)
    def test_validate_strategy_exception_failure(
        self,
        mock_civilization: MagicMock,
        mock_planet_create: MagicMock,
        mock_logger_error: MagicMock,
    ):
        mock_civilization.side_effect = [self.civ1, self.civ2]
        mock_strategy = MagicMock(
            side_effect=Exception("simulated exception error"))

        assert CivilizationService.validate_strategy(mock_strategy) is False
        assert mock_civilization.call_args_list == [
            call(name="Self", strategy=ANY, resources=0),
            call(name="TestOpponent", strategy=ANY, resources=0),
        ]
        mock_planet_create.assert_called_once_with(
            name="TestPlanet", cost=Cost.HIGH)
        mock_strategy.assert_called_once_with(
            self=self.civ1,
            planet=mock_planet_create.return_value,
            opponent=self.civ2,
        )
        assert mock_logger_error.call_args_list == [
            call('-' * 80),
            call(mock_strategy.side_effect, exc_info=True),
            call('-' * 80),
        ]
