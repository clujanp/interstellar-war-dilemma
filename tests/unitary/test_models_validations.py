import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock
from app.core.domain.models.validations import SkirmishValidations
from app.core.domain.models import Civilization, Planet


class TestSkirmishValidations(TestCase):
    def setUp(self):
        self.civilization_1 = MagicMock(spec=Civilization)
        self.civilization_2 = MagicMock(spec=Civilization)
        self.planet = MagicMock(spec=Planet)
        self.data = {
            'civilization_1': self.civilization_1,
            'civilization_2': self.civilization_2,
            'planet': self.planet
        }

    def test_validate_civilizations_success(self):
        self.civilization_1.configure_mock(name='Civ1')
        self.civilization_2.configure_mock(name='Civ2')
        result = SkirmishValidations.validate_civilizations(self.data)
        assert result == self.data

    def test_validate_civilizations_fail(self):
        self.data['civilization_2'] = self.data['civilization_1']
        with self.assertRaises(ValueError) as context:
            SkirmishValidations.validate_civilizations(self.data)
        assert "Civilizations must be different" == str(context.exception)

    def test_validate_planet_success(self):
        self.planet.configure_mock(cost=50, colonized=False)
        self.civilization_1.configure_mock(resources=100)
        self.civilization_2.configure_mock(resources=100)
        skirmish = SkirmishValidations()
        skirmish.planet = self.planet
        skirmish.civilization_1 = self.civilization_1
        skirmish.civilization_2 = self.civilization_2
        result = skirmish.validate_planet()

        assert result == skirmish

    def test_validate_planet_fail_not_enough_resources(self):
        self.planet.configure_mock(cost=150, colonized=False)
        self.civilization_1.configure_mock(resources=100)
        self.civilization_2.configure_mock(resources=100)
        skirmish = SkirmishValidations()
        skirmish.planet = self.planet
        skirmish.civilization_1 = self.civilization_1
        skirmish.civilization_2 = self.civilization_2

        with self.assertRaises(ValueError) as context:
            skirmish.validate_planet()
        assert (
            "Not enough resources to colonize the planet"
            == str(context.exception)
        )

    def test_validate_planet_fail_already_colonized(self):
        self.planet.configure_mock(cost=50, colonized=True)
        self.civilization_1.configure_mock(resources=100)
        self.civilization_2.configure_mock(resources=100)
        skirmish = SkirmishValidations()
        skirmish.planet = self.planet
        skirmish.civilization_1 = self.civilization_1
        skirmish.civilization_2 = self.civilization_2

        with self.assertRaises(ValueError) as context:
            skirmish.validate_planet()
        assert "Planet already colonized" == str(context.exception)
