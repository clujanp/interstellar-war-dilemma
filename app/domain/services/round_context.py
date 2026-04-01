from random import shuffle, choice as random_choice
from typing import Optional, Type
from types import TracebackType

from app.domain.models import AstronomyBody, Civilization, Round, Skirmish, Match
from app.domain.value_objects import (
    AstronomicObjectType as AstroType, Decision, Resources)
from app.interfaces.db import RoundRepository


class RoundContext:
    """Context manager for a single round.

    On enter: generates astro bodies, creates pairings, accepts decisions.
    On exit: finalizes, resolves, updates scores, persists.
    """
    
    ASTRO_BODIES_RESOURCES = range(1, 11)

    def __init__(
        self,
        civilizations: list[Civilization],
        match: Match,
        round_repo: RoundRepository,
    ) -> None:
        self._civilizations = civilizations
        self._match = match
        self._round = None
        self._round_repo = round_repo

    @property
    def round(self) -> Round:
        if self._round is None:
            raise RuntimeError("Round not started. Use within 'with' block.")
        return self._round

    def __enter__(self) -> Round:
        return self._setup()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        if exc_type is None:
            self._finalize_decisions()
            self._resolve()
            self._round_repo.save(self.round)

    def set_decision(self, civilization: Civilization, decision: Decision) -> None:
        """Submit a decision for a civilization in this round."""
        for skirmish in self.round.skirmishes:
            if skirmish.civ_a.id == civilization.id:
                skirmish.decision_a = decision
                return
            if skirmish.civ_b.id == civilization.id:
                skirmish.decision_b = decision
                return

    def _setup(self) -> Round:
        """Generate astro bodies and create 1-on-1 pairings."""
        civs = self._suffle_civilizations(self._civilizations)
        num_pairs = len(civs) // 2
        astro_bodies = self._generate_astro_bodies(num_pairs)
        skirmishes = [Skirmish(
            civ_a=civs[i],
            civ_b=civs[i + 1],
            astronomical_object=astro_bodies[i // 2],
        ) for i in range(0, len(civs), 2)]

        self._round = Round(
            match=self._match,
            number=self._match.current_round,
            skirmishes=skirmishes,
        )
        return self._round

    def _finalize_decisions(self) -> None:
        """Apply NOT_DECIDED fallback for missing decisions."""
        for skirmish in self.round.skirmishes:
            if skirmish.decision_a is None:
                skirmish.decision_a = Decision.NOT_DECIDED
            if skirmish.decision_b is None:
                skirmish.decision_b = Decision.NOT_DECIDED

    def _resolve(self) -> None:
        """Resolve all skirmishes in the round."""
        for skirmish in self.round.skirmishes:
            skirmish.resolve()

    @staticmethod
    def _suffle_civilizations(civs: list[Civilization]) -> list[Civilization]:
        """Return a new list of civilizations in random order."""
        shuffle(civs := list(civs))
        return civs

    @staticmethod
    def _generate_astro_bodies(count: int) -> list[AstronomyBody]:
        """Generate random astro bodies for pairings."""
        return [AstronomyBody(
            type=AstroType.PLANET,
            resources=Resources(
                random_choice(RoundContext.ASTRO_BODIES_RESOURCES)),
        ) for _ in range(count)]
