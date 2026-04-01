from random import shuffle

from app.domain.models import Civilization, Match, Round, Skirmish, AstronomyBody
from app.domain.value_objects import Decision


class RoundService:
    """Stateless domain service for round-level operations."""

    def setup_round(
        self, match: Match, astro_bodies: list[AstronomyBody]
    ) -> Round:
        """Generate a round with 1-on-1 pairings.

        Each civilization appears in exactly one skirmish per round.
        Civilizations are shuffled then paired sequentially: (0,1), (2,3), ...
        The caller (GameEngine) must ensure an even number of civilizations.
        Astronomical bodies are assigned round-robin from the provided pool.
        """
        civs = list(match.civilizations)
        shuffle(civs)
        skirmishes = [
            Skirmish(
                civ_a=civs[i],
                civ_b=civs[i + 1],
                astronomical_object=astro_bodies[(i // 2) % len(astro_bodies)],
            ) for i in range(0, len(civs), 2)
        ]
        return Round(number=match.current_round, skirmishes=skirmishes)

    def propagate_decision(
        self, round: Round, civilization: Civilization, decision: Decision,
    ) -> None:
        """Set a civilization's decision on its skirmish in this round."""
        for skirmish in round.skirmishes:
            if skirmish.civ_a.id == civilization.id:
                skirmish.decision_a = decision
                return
            if skirmish.civ_b.id == civilization.id:
                skirmish.decision_b = decision
                return

    def resolve_round(self, round: Round) -> Round:
        """Resolve all skirmishes in the round."""
        for skirmish in round.skirmishes:
            skirmish.resolve()
        return round
