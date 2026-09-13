from unittest import TestCase
from app.core.domain.models import AstroBody
from app.core.domain.value_objects import (
    AstroKind, ColonizeCost, AstroBodyProduction,)


class TestAstroBody(TestCase):
    """Unit tests for the AstroBody model."""

    def test_init_astro_body(self):
        """Test the initialization of an astro body."""
        astro_body = AstroBody(
            name=AstroBody.name_generator(),
            kind=AstroKind.PLANET,
            colonize_cost=ColonizeCost.HOSTILE,
            production=AstroBodyProduction.HIGH,
        )
        assert astro_body.name is not None
        assert astro_body.kind == "planet"
        assert astro_body.colonize_cost == 4
        assert astro_body.production == 3
        assert astro_body.status == "available"
