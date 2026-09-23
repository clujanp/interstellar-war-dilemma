from collections import OrderedDict
from itertools import combinations, cycle
from unittest import TestCase
from app.core.domain.models import Skirmish, AstroBody
from app.core.domain.value_objects import (
    Resources, Decision, ColonizeCost, AstroBodyProduction, SkirmishResult,
    Efficiency)
from app.core.game.models import CivilizationRegistration, SkirmishRelated
from app.core.game.repositories.skirmishes import SkirmishesRepo
from app.core.game.repositories.interfaces import ISkirmishesRepo


class TestSkirmishesRepo(TestCase):
    """Test suite for the SkirmishesRepo class."""

    def setUp(self):
        self.players = [CivilizationRegistration(
            name=f"Player{i}",
            resources=Resources(100),
            callback=lambda *_, **__: Decision.ATTACK,  # callback dummy
        ) for i in range(3)]
        self.astros = [AstroBody(
            name=AstroBody.name_generator(),
            kind="planet",
            colonize_cost=ColonizeCost.HOSTILE,
            production=AstroBodyProduction.HIGH,
        ) for _ in range(9)]

        # (A,B), (A,C), (B,C), again (A,B), ...
        twin_players_generator = cycle(combinations(self.players, 2))
        self.skirmishes = []
        for astro in self.astros:
            players = next(twin_players_generator)
            (skirmish := Skirmish(
                civilizations=tuple(players),
                astro_body=astro,
                decisions=[Decision.ATTACK, Decision.COOPERATE],
            )).resolve()
            for player in players:
                self.skirmishes.append(SkirmishRelated(owner=player, skirmish=skirmish))

    def test_interface(self):
        """Test that SkirmishesRepo has the correct interface."""
        assert issubclass(SkirmishesRepo, ISkirmishesRepo)

    def test_initialization(self):
        """Test that the SkirmishesRepo can be initialized."""
        repo = SkirmishesRepo()
        # pylint: disable=protected-access
        assert repo._SkirmishesRepo__skirmishes == OrderedDict()

    def test_record(self):
        """Test that a skirmish can be recorded in the repository."""
        repo = SkirmishesRepo()
        for skirmish in self.skirmishes:
            repo.record(skirmish)
        # pylint: disable=protected-access
        assert len(repo._SkirmishesRepo__skirmishes) == 3  # 3 players
        assert len([  # 9 planets/skirmishes x 2 owners = 18 skirmishes related
            skirmish
            for skirmish_list in repo._SkirmishesRepo__skirmishes.values()
            for skirmish in skirmish_list
        ]) == 18
        assert repo._SkirmishesRepo__skirmishes[self.players[0]] == [
            skirmish
            for skirmish in self.skirmishes
            if skirmish.owner == self.players[0]
        ]

    def test_record_type_error(self):
        """Test that recording a non-SkirmishRelated raises a TypeError."""
        repo = SkirmishesRepo()
        with self.assertRaises(TypeError) as error:
            repo.record("not a skirmish related instance")
        assert str(error.exception) == "Expected a SkirmishRelated instance."

    def test_list(self):
        """Test that all recorded skirmishes can be listed."""
        repo = SkirmishesRepo()
        for skirmish in self.skirmishes:
            repo.record(skirmish)
        all_skirmishes = repo.list()
        assert len(all_skirmishes) == 18
        assert set(all_skirmishes) == set(self.skirmishes)

    def test_query(self):
        """Test that skirmishes can be queried from the repository."""
        repo = SkirmishesRepo()
        for skirmish in self.skirmishes:
            repo.record(skirmish)

        for player in self.players:
            assert len(repo.query(owner=player)) == 6

        assert all([
            skirmish.owner == self.players[0]
            and skirmish.decision == Decision.ATTACK
            and skirmish.opponent_decision == Decision.COOPERATE
            and skirmish.result == SkirmishResult.TREASON_A
            and skirmish.gain_factor == float(Efficiency.TREASON)
            for skirmish in repo.query(owner=self.players[0])
        ])

    def test_query_with_filters(self):
        """Test that skirmishes can be queried with specific filters."""
        repo = SkirmishesRepo()
        for skirmish in self.skirmishes:
            repo.record(skirmish)

        filtered_skirmishes = repo.query(
            owner=self.players[0], opponent="Player2")

        assert len(filtered_skirmishes) == 3
        assert all([
            skirmish.opponent == "Player2" for skirmish in filtered_skirmishes])

    def test_get_all_astro_bodies(self):
        """Test that all astro involved in skirmishes can be retrieved."""
        repo = SkirmishesRepo()
        for skirmish in self.skirmishes:
            repo.record(skirmish)
        all_astro_bodies = repo.get_all_astro_bodies()
        expected_astro_bodies = set(
            skirmish.skirmish.astro_body for skirmish in self.skirmishes)
        assert all_astro_bodies == expected_astro_bodies
