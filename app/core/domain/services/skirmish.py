from typing import List, Tuple
from app.core.domain.models import (
    Score, Position, Planet, Civilization, Skirmish)


class SkirmishService:
    @staticmethod
    def create(
        planet: Planet,
        civilization_1: Civilization,
        civilization_2: Civilization
    ) -> Skirmish:
        return Skirmish(
            planet=planet,
            civilization_1=civilization_1,
            civilization_2=civilization_2,
        )

    @staticmethod
    def results(skirmish: Skirmish) -> Tuple[List[Civilization], Score, Score]:
        return skirmish.winner_, skirmish.score_1, skirmish.score_2

    @classmethod
    def resolve(
        cls, skirmish: Skirmish
    ) -> Tuple[List[Civilization], Score, Score]:
        if skirmish.winner_ is not None:
            raise ValueError(ERR_MSG['already_resolved'])

        planet = skirmish.planet
        civilization_1 = skirmish.civilization_1
        civilization_2 = skirmish.civilization_2

        skirmish.posture_1 = civilization_1.strategy(
            self=civilization_1, planet=planet, opponent=civilization_2)
        skirmish.posture_2 = civilization_2.strategy(
            self=civilization_2, planet=planet, opponent=civilization_1)

        if all([skirmish.posture_1, skirmish.posture_2]):
            return cls._decide_winner(skirmish, Score.TIE_GOOD, Score.TIE_GOOD)
        if not any([skirmish.posture_1, skirmish.posture_2]):
            return cls._decide_winner(skirmish, Score.TIE_BAD, Score.TIE_BAD)
        if skirmish.posture_1 is Position.AGGRESSION:
            return cls._decide_winner(skirmish, Score.WIN, Score.LOSE)
        return cls._decide_winner(skirmish, Score.LOSE, Score.WIN)

    @staticmethod
    def _decide_winner(
        skirmish: Skirmish, score_1: Score, score_2: Score
    ) -> Tuple[List[Civilization], Score, Score]:
        if score_1 == score_2:
            winners = [skirmish.civilization_1, skirmish.civilization_2]
        elif score_1 > score_2:
            winners = [skirmish.civilization_1]
        else:
            winners = [skirmish.civilization_2]

        skirmish.score_1 = score_1
        skirmish.score_2 = score_2
        skirmish.winner_ = winners
        skirmish.planet.colonizer = skirmish.winner_
        return winners, score_1, score_2
