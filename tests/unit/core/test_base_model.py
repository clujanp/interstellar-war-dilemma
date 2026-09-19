from unittest import TestCase
from ulid import ULID
from app.core.base_model import CustomBaseModel


class TestBaseModel(TestCase):
    """Unit tests for the BaseModel class."""

    def setUp(self):
        class Player(CustomBaseModel):
            ...

        self.model = Player

    def test_id(self):
        """Test that the BaseModel has an ID attribute."""
        player = self.model()
        assert hasattr(player, "id") and isinstance(player.id, ULID)

    def test_id_is_unique(self):
        """Test that each instance of the BaseModel has a unique ID."""
        player1 = self.model()
        player2 = self.model()
        assert player1.id != player2.id

    def test_hasheable(self):
        """Test that the BaseModel instances are hashable."""
        player_1 = self.model()
        player_2 = self.model()
        assert isinstance(hash(player_1), int)
        assert isinstance(hash(player_2), int)
        assert hash(player_1) != hash(player_2)
        try:
            {player_1: "value"}
        except TypeError:
            self.fail("BaseModel instance is not hashable")
