from typing import List, Tuple
from app.core.domain.models import (
    Score, Position, Planet, Civilization, Skirmish)
from app.config.messages import ERR_SKIRMISH_SERVICE as ERR_MSG


class SkirmishService:
    RESOLUTER = {
        (Position.COOPERATION, Position.COOPERATION,):
            lambda civ1, civ2: ((civ1, civ2,), Score.TIE_GOOD, Score.TIE_GOOD),
        (Position.COOPERATION, Position.AGGRESSION,):
            lambda civ1, civ2: ((civ2,), Score.LOSE, Score.WIN),
        (Position.AGGRESSION, Position.COOPERATION,):
            lambda civ1, civ2: ((civ1,), Score.WIN, Score.LOSE),
        (Position.AGGRESSION, Position.AGGRESSION,):
            lambda civ1, civ2: ((civ1, civ2,), Score.TIE_BAD, Score.TIE_BAD),
        # fail cases
        (Position.FAIL, Position.COOPERATION,):
            lambda civ1, civ2: ((civ2,), Score.LOSE, Score.TIE_GOOD),
        (Position.COOPERATION, Position.FAIL,):
            lambda civ1, civ2: ((civ1,), Score.TIE_GOOD, Score.LOSE),
        (Position.FAIL, Position.AGGRESSION,):
            lambda civ1, civ2: ((civ2,), Score.LOSE, Score.MAX_SCORE),
        (Position.AGGRESSION, Position.FAIL,):
            lambda civ1, civ2: ((civ1,), Score.MAX_SCORE, Score.LOSE),
        (Position.FAIL, Position.FAIL,):
            lambda civ1, civ2: (tuple(), Score.LOSE, Score.LOSE),
    }

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
    ) -> Tuple[Tuple[Civilization], Score, Score]:
        if skirmish.winner_ is not None:
            raise ValueError(ERR_MSG['already_resolved'])

        planet = skirmish.planet
        civilization_1 = skirmish.civilization_1
        civilization_2 = skirmish.civilization_2

        skirmish.posture_1 = civilization_1.strategy(
            self=civilization_1, planet=planet, opponent=civilization_2)
        skirmish.posture_2 = civilization_2.strategy(
            self=civilization_2, planet=planet, opponent=civilization_1)

        return cls._decide_winner(skirmish)

    @classmethod
    def _decide_winner(
        cls, skirmish: Skirmish
    ) -> Tuple[Tuple[Civilization], Score, Score]:
        resoluter = cls.RESOLUTER.get(
            (skirmish.posture_1, skirmish.posture_2,))

        skirmish.winner_, skirmish.score_1, skirmish.score_2 = resoluter(
            skirmish.civilization_1, skirmish.civilization_2)
        skirmish.planet.colonizer = skirmish.winner_
        return skirmish.winner_, skirmish.score_1, skirmish.score_2
