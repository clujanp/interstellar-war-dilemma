from random import choice
from typing import Sequence
from unittest import TestCase
from app.core.domain.models import AstroBody, Civilization, Skirmish
from app.core.domain.value_objects import (
    AstroBodyProduction, AstroKind, CivilizationStatus, ColonizeCost,
    Decision, Efficiency, Resources, SkirmishStatus, SkirmishResult,)


class TestBaseGameLifeCycleIntegration(TestCase):
    """Integration test for the base game life cycle."""

    def setUp(self):
        self.civ_a = Civilization(name="Civ A", resources=Resources(10))
        self.civ_b = Civilization(name="Civ B", resources=Resources(10))
        self.astro_bodies = [
            AstroBody(
                name=AstroBody.name_generator(),
                kind=choice(list(AstroKind)),
                colonize_cost=choice(list(ColonizeCost)),
                production=choice(list(AstroBodyProduction)),
            ) for _ in range(5)
        ]

    # Logic helpers

    @classmethod
    def next_name(cls, astro_bodies: list[AstroBody], new_name: str) -> str:
        """Generate the next available name for an astro body,
        ensuring it is unique among the given list of astro bodies."""
        next_index = 0
        for astro in astro_bodies:
            if new_name in astro.name:
                next_index += 1
        return f"{new_name} {next_index}" if next_index > 0 else new_name

    @classmethod
    def pay_colonize_cost(
        cls, civs: Sequence[Civilization], astro_body: AstroBody
    ) -> None:
        """Handler for paying the colonize cost of an astro body by a civ."""
        for civ in civs:
            civ.resources -= astro_body.colonize_cost

    @classmethod
    def set_decisions_in_skirmish(
        cls, civ: Civilization, skirmish: Skirmish, decision: Decision
    ) -> None:
        """Handler for set decision of civ in a skirmish."""
        try:
            index_civ = skirmish.civilizations.index(civ)
        except ValueError as err:
            raise ValueError("Civilization not found in skirmish.") from err
        skirmish.decisions[index_civ] = decision

    @classmethod
    def apply_skirmish_production(cls, skirmishes: list[Skirmish]) -> None:
        """Handler for apply the production of all astro bodies
        in a list of skirmishes for related civilization."""
        for skirmish in skirmishes:
            astro_production = skirmish.astro_body.production
            civ_a, civ_b = skirmish.civilizations
            civ_a_part, civ_b_part = skirmish.production_participation
            civ_a.resources += astro_production * civ_a_part
            civ_b.resources += astro_production * civ_b_part

    @classmethod
    def dead_guard(
        cls,
        civs: Sequence[Civilization],
        memory: dict[Civilization, int],
        threshold: int,
    ) -> Sequence[Civilization]:
        """Handler for define civs to kill using a external memory
        and a threshold for limit counts of declining state."""
        civs_to_kill = []
        for civ in filter(
            lambda c: c.status == CivilizationStatus.DECLINING, civs
        ):
            memory[civ] = memory.get(civ, 0) + 1
            if memory.get(civ, 0) >= threshold:
                civs_to_kill.append(civ)
        return civs_to_kill

    def test_init_astro_body_with_already_assigned_name(self):
        """Test the inti of an astro body with an already assigned name."""
        astro_bodies = []
        for i in range(3):
            name = self.next_name(astro_bodies, 'TestName')
            astro_bodies.append(
                astro := AstroBody(
                    name=name,
                    kind=choice(list(AstroKind)),
                    colonize_cost=choice(list(ColonizeCost)),
                    production=choice(list(AstroBodyProduction)),
                )
            )
            assert (
                astro.name == 'TestName' if i <= 0
                else astro.name == f"TestName {i}"
            )

    def test_pay_colonize_cost(self):
        """Test paying the colonize cost for an astro body."""
        for astro_body in self.astro_bodies:
            for civ in (self.civ_a, self.civ_b):
                self.pay_colonize_cost([civ], astro_body)

        all_colonize_cost = sum(
            astro_body.colonize_cost for astro_body in self.astro_bodies)
        assert self.civ_a.resources == 10 - all_colonize_cost
        assert self.civ_b.resources == 10 - all_colonize_cost

    def test_take_decisions_in_skirmish(self):
        """Test taking decisions in a skirmish."""
        skirmish = Skirmish(
            civilizations=(self.civ_a, self.civ_b),
            astro_body=self.astro_bodies[0],
        )
        self.set_decisions_in_skirmish(
            self.civ_a, skirmish, Decision.COOPERATE)
        self.set_decisions_in_skirmish(
            self.civ_b, skirmish, Decision.ATTACK)

        assert skirmish.decisions == [Decision.COOPERATE, Decision.ATTACK]

    def test_resolve_skirmish(self):
        """Test resolving a skirmish after decisions have been made."""
        skirmish = Skirmish(
            civilizations=(self.civ_a, self.civ_b),
            astro_body=self.astro_bodies[0],
        )
        skirmish.decisions = [Decision.COOPERATE, Decision.ATTACK]
        skirmish.resolve()

        assert isinstance(skirmish.decisions, tuple) and (
            skirmish.decisions == (Decision.COOPERATE, Decision.ATTACK))
        assert skirmish.status == SkirmishStatus.FINISHED
        assert skirmish.result == SkirmishResult.TREASON_B
        assert skirmish.production_participation == (
            Efficiency.NONE, Efficiency.TREASON)

    def test_resolve_many_skirmishes(self):
        """Test resolving many skirmishes in sequence."""
        (skirmish_1 := Skirmish(
            civilizations=(self.civ_a, self.civ_b),
            astro_body=self.astro_bodies[0],
            decisions=[Decision.COOPERATE, Decision.ATTACK]
        )).resolve()
        (skirmish_2 := Skirmish(
            civilizations=(self.civ_a, self.civ_b),
            astro_body=self.astro_bodies[1],
            decisions=[Decision.ATTACK, Decision.ATTACK]
        )).resolve()
        (skirmish_3 := Skirmish(
            civilizations=(self.civ_a, self.civ_b),
            astro_body=self.astro_bodies[2],
            decisions=[Decision.COOPERATE, Decision.COOPERATE]
        )).resolve()

        for skirmish, result, parts in zip(
            (skirmish_1, skirmish_2, skirmish_3,), (
                SkirmishResult.TREASON_B,
                SkirmishResult.CONFLICT,
                SkirmishResult.COOPERATION,
            ), (
                (Efficiency.NONE, Efficiency.TREASON),
                (Efficiency.CONFLICT, Efficiency.CONFLICT),
                (Efficiency.COOPERATION, Efficiency.COOPERATION),
            )
        ):
            with self.subTest(skirmish=skirmish.result, result=result):
                assert skirmish.status == SkirmishStatus.FINISHED
                assert skirmish.result == result
                assert skirmish.production_participation == parts

    def test_calculate_production_generation(self):
        """Test calc the production generation after resolving a skirmish."""
        skirmishes = [
            skirmish_1 := Skirmish(
                civilizations=(self.civ_a, self.civ_b),
                astro_body=self.astro_bodies[0],
            ),
            skirmish_2 := Skirmish(
                civilizations=(self.civ_a, self.civ_b),
                astro_body=self.astro_bodies[1],
            ),
        ]
        skirmish_1.decisions = [Decision.COOPERATE, Decision.ATTACK]
        skirmish_1.resolve()
        skirmish_2.decisions = [Decision.ATTACK, Decision.ATTACK]
        skirmish_2.resolve()

        self.apply_skirmish_production(skirmishes)

        assert self.civ_a.resources == (
            Resources(10)
            + self.astro_bodies[0].production * Efficiency.NONE  # 0 Resources
            + self.astro_bodies[1].production * Efficiency.CONFLICT)
        assert self.civ_b.resources == (
            Resources(10)
            + self.astro_bodies[0].production * Efficiency.TREASON
            + self.astro_bodies[1].production * Efficiency.CONFLICT)

    def test_civ_life_cicle(self):
        """Test the life cycle of a civilization."""
        civ_1 = Civilization(name="Republic", resources=Resources(5))
        civ_2 = Civilization(name="Maverics", resources=Resources(1))
        epochs = []
        memory_civs_falling: dict[Civilization, int] = {}

        # Epochs
        for epoch_index, desicions, astro_body in zip(range(5), (
            # 3 Attacks for ensure fall of civ_2
            [Decision.ATTACK, Decision.COOPERATE],
            [Decision.ATTACK, Decision.COOPERATE],
            [Decision.ATTACK, Decision.COOPERATE],
            [Decision.ATTACK, Decision.ATTACK],
            [Decision.COOPERATE, Decision.COOPERATE],
        ), self.astro_bodies):
            all_skirmishes = [
                skirmish for epoch in epochs
                for skirmish in epoch["skirmishes"]
            ]
            self.apply_skirmish_production(all_skirmishes)

            # Kill a civ when the threshold of declining epochs is exceeded
            civs_to_kill = self.dead_guard(
                (civ_1, civ_2), memory_civs_falling, threshold=2)
            if civs_to_kill:
                # Manage a civ to kill
                break

            # Paid colonization cost
            self.pay_colonize_cost([civ_1, civ_2], astro_body)

            epochs.append({
                "index": epoch_index,
                "civilizations": (civ_1, civ_2),
                "skirmishes": [
                    (skirmish := Skirmish(
                        civilizations=(civ_1, civ_2), astro_body=astro_body)),
                ],
            })
            self.set_decisions_in_skirmish(civ_1, skirmish, desicions[0])
            self.set_decisions_in_skirmish(civ_2, skirmish, desicions[1])
            skirmish.resolve()
