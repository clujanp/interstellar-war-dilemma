from unittest import TestCase
from app.core.domain.models import Civilization
from app.core.domain.value_objects import Resources


class TestCivilizatio (TestCase):
    """Unit tests for the Civilization model."""

    def test_init_civilization(self):
        """Test the initialization of a civilization."""
        civilization = Civilization(
            name="Test Civilization",
            resources=Resources(100),
        )
        assert civilization.name == "Test Civilization"
        assert civilization.resources == 100
        assert civilization.status == "alive"

    def test_civ_no_enough_resources_change_on_declining(self):
        """Test that a civ with insufficient resources becomes declining."""
        poor_civ = Civilization(name="Poor Civ", resources=Resources(1))
        poor_civ.resources -= 1
        assert poor_civ.status == "declining"
        assert poor_civ.resources == 0

    def test_civ_recovers_when_resources_positive(self):
        """Test that a declining civ recovers when have resources."""
        civ = Civilization(name="Recovering Civ", resources=Resources(0))
        civ.resources += 10
        assert civ.status == "alive"
        assert civ.resources == 10
