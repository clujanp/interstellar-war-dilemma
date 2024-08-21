from typing import List, Tuple
from app.core.domain.models import Civilization, Skirmish, Round
from random import choices


class RoundService:
    @staticmethod
    def create(number: int, skirmishes: List[Skirmish]) -> Round:
        return Round(number=number, skirmishes=skirmishes)

    @staticmethod
    def decide_opponents(
        civilizations: List[Civilization]
    ) -> List[Tuple[Civilization, Civilization]]:
        assert len(civilizations) % 2 == 0, "Invalid number of civilizations"

        done = []
        opponents = []
        for civilization in civilizations:
            if civilization not in done:
                odds = {
                    opponent: (
                        (civilization.memory.length + 1)
                        - civilization.memory.skirmishes_count(opponent)
                    )
                    for opponent in civilizations
                    if opponent != civilization and opponent not in done
                }
                options, weights = zip(*odds.items())
                opponent = choices(options, weights=weights, k=1)[0]
                opponents.append((civilization, opponent,))
                done.append(civilization)
                done.append(opponent)
        return opponents
