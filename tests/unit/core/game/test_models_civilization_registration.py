from unittest import TestCase
from pydantic import ValidationError
from app.core.game.models import CivilizationRegistration
from app.core.game.models import Civilization
from app.core.domain.value_objects import Resources, Decision


class TestCivilizationRegistration(TestCase):
    """Test suite for the CivilizationRegistration class."""

    def test_initialization(self):
        """Test that a CivilizationRegistration instance can be initialized."""
        civ = CivilizationRegistration(
            name="TestCiv",
            resources=Resources(100),
            callback=lambda *_, **__: Decision.ATTACK,
        )

        assert isinstance(civ, CivilizationRegistration)
        assert isinstance(civ, Civilization)
        assert callable(civ.callback)
        assert civ.name == "TestCiv"
        assert civ.resources == 100
        assert civ.callback() == Decision.ATTACK

    def test_callback_not_callable(self):
        """Test that initializing with a non-callable callback raises an error."""
        with self.assertRaises(ValidationError) as error:
            CivilizationRegistration(
                name="TestCiv",
                resources=Resources(100),
                callback="not_callable",
            )
        assert (
            "1 validation error for CivilizationRegistration\n"
            "callback"
        ) in str(error.exception)
