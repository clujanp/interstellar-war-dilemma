import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.core.domain.models import (
    Civilization, Planet, Skirmish, Memories, Score, Position)


class TestModelPlanet(TestCase):
    def setUp(self):
        self.planet = Planet(name="TestPlanet", cost=2)
        self.civilization = MagicMock()
        self.civilization.name = "ColonizerCiv"

    def test_initialization_success(self):
        assert self.planet.name == "TestPlanet"
        assert self.planet.cost == 2
        assert self.planet.colonized is False
        assert self.planet.colonizer is None

    def test_colonizer_name_success(self):
        assert self.planet.colonizer_name == '<nobody>'
        self.planet.colonizer = [self.civilization]
        assert self.planet.colonizer_name == "ColonizerCiv"

    def test_str_success(self):
        assert "TestPlanet is colonized by '<nobody>'" == str(self.planet)

    def test_str_colonizer_success(self):
        self.planet.colonizer = [self.civilization]
        assert "TestPlanet is colonized by 'ColonizerCiv'" == str(self.planet)


class TestModelCivilization(TestCase):
    def setUp(self):
        self.strategy = MagicMock(return_value=True)
        self.civilization = Civilization(
            name="TestCiv", strategy=self.strategy, resources=10)

    def test_civilization_initialization_success(self):
        assert self.civilization.name == "TestCiv"
        assert self.civilization.resources == 10
        assert self.civilization.memory.owner is None

    def test_str_success(self):
        assert "TestCiv has 10 resources" == str(self.civilization)


class TestModelSkirmish(TestCase):
    def setUp(self):
        self.planet = Planet(name="TestPlanet", cost=2)
        self.civ1 = Civilization(
            name="Civ1",
            strategy=MagicMock(return_value=Position.COOPERATION),
            resources=10
        )
        self.civ2 = Civilization(
            name="Civ2",
            strategy=MagicMock(return_value=Position.AGGRESSION),
            resources=10
        )
        self.skirmish = Skirmish(
            planet=self.planet,
            civilization_1=self.civ1,
            civilization_2=self.civ2,
            posture_1=True,
            posture_2=False,
            winner_=[self.civ2],
            score_1=Score.LOSE,
            score_2=Score.WIN,
        )

    def test_skirmish_initialization_success(self):
        assert self.skirmish.planet == self.planet
        assert self.skirmish.civilization_1 == self.civ1
        assert self.skirmish.civilization_2 == self.civ2
        assert self.skirmish.posture_1 is True
        assert self.skirmish.posture_2 is False
        assert self.skirmish.winner_ == [self.civ2]
        assert self.skirmish.score_1 == Score.LOSE
        assert self.skirmish.score_2 == Score.WIN

    def test_behavior_civilization_1_success(self):
        response = self.skirmish.behavior(self.civ1)
        assert (Position.COOPERATION, Score.LOSE) == response

    def test_behavior_civilization_2_success(self):
        response = self.skirmish.behavior(self.civ2)
        assert (Position.AGGRESSION, Score.WIN) == response

    def test_behavior_civilization_fail(self):
        with self.assertRaises(ValueError) as context:
            self.skirmish.behavior(MagicMock())
        assert "Civilization not in the skirmish" in str(context.exception)

    def test_str_success(self):
        assert (
            "Skirmish in 'TestPlanet' with winner Civ2" == str(self.skirmish))

    def test_str_disputing_success(self):
        self.skirmish.winner_ = None
        assert "Skirmish in 'TestPlanet' is disputing" == str(self.skirmish)


class TestModelMemories(TestCase):
    def setUp(self):
        self.civilization_1 = Civilization(
            name="TestCiv1", strategy=MagicMock(), resources=10)
        self.civilization_2 = Civilization(
            name="TestCiv2", strategy=MagicMock(), resources=10)
        self.memories = Memories(owner=self.civilization_1)
        self.tie_good = (Position.COOPERATION, Score.TIE_GOOD,)
        self.tie_bad = (Position.AGGRESSION, Score.TIE_BAD,)
        self.skirmishes = [
            MagicMock(
                _winner=[self.civilization_1, self.civilization_2],
                behavior=MagicMock(return_value=self.tie_good),
            ),
            MagicMock(
                _winner=[self.civilization_2],
                behavior=MagicMock(return_value=self.tie_bad),
            ),
        ]

    def test_memories_initialization_success(self):
        assert self.memories.owner == self.civilization_1
        assert self.memories.memories_ == []

    @patch('app.core.domain.models.Memories.skirmishes')
    def test_add_memory_success(self, mock_skirmishes_method: MagicMock):
        skirmish = MagicMock()
        self.memories.add(skirmish)
        mock_skirmishes_method.cache_clear.assert_called()
        assert skirmish in self.memories.memories_

    def test_skirmishes(self):
        self.memories.owner = None
        self.memories.memories_ = self.skirmishes
        expected = {
            self.civilization_1: [self.tie_good],
            self.civilization_2: [self.tie_good, self.tie_bad],
        }
        response = self.memories.skirmishes()
        assert expected == response

    def test_skirmishes_with_owner(self):
        self.memories.memories_ = self.skirmishes
        expected = {
            self.civilization_2: [self.tie_good, self.tie_bad],
        }
        response = self.memories.skirmishes()
        assert expected == response

    def test_civilizations(self):
        self.memories.owner = None
        self.memories.memories_ = self.skirmishes
        response = self.memories.civilizations
        assert all([
            civilization in [
                self.civilization_1, self.civilization_2, self.civilization_3]
            for civilization in response
        ])

    def test_civilizations_without_memories_owner(self):
        self.memories.owner = self.civilization_1
        self.memories.memories_ = self.skirmishes
        response = self.memories.civilizations
        assert all([
            civilization in [self.civilization_2, self.civilization_3]
            for civilization in response
        ])

    def test_str_success(self):
        assert "TestCiv1's Memories of 0 skirmishes" == str(self.memories)

    def test_str_no_owner_success(self):
        self.memories.owner = None
        assert "Memories of 0 skirmishes" == str(self.memories)
