import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.core.domain.services import CivilizationService


class TestCivilizationService(TestCase):
    def setUp(self):
        self.strategy = MagicMock(return_value=True)
        self.civ1 = MagicMock(name="Self")
        self.civ2 = MagicMock(name="TestOpponent")

    @patch('app.core.domain.models.models.Memories')
    @patch('app.core.domain.services.civilization.MemoriesServiceWrapper')
    def test_create_civilization_success(
        self,
        mock_memories_wrapper: MagicMock,
        mock_memories: MagicMock,
    ):
        civilization = CivilizationService.create(
            name="TestCiv",
            strategy=self.strategy,
            resources=10,
        )
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
    def test_create_civilization_skip_validateion_success(
        self,
        mock_memories_wrapper: MagicMock,
        mock_memories: MagicMock,
    ):
        civilization = CivilizationService.create(
            name="TestCiv",
            strategy=self.strategy,
            resources=10,
        )
        assert civilization.name == "TestCiv"
        assert civilization.resources == 10
        assert (
            civilization.memory.owner
            == mock_memories_wrapper.return_value.owner
        )
