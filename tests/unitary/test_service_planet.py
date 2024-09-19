import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.core.domain.models import Cost
from app.core.domain.services import PlanetService


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
            cost=Cost.HIGH
        )
        mock_planet_namer.assert_not_called()
        assert planet.name == "CustomPlanet"
        assert planet.cost == Cost.HIGH
