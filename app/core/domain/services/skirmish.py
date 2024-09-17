from typing import List, Tuple, Dict, Callable
from app.core.domain.models import (
    Score, Position, Result, Planet, Civilization, Skirmish)
from app.config.messages import ERR_SKIRMISH_SERVICE as ERR_MSG


class SkirmishService:
    def __init__(self, resoluter: Dict[Tuple[Position, Position], Callable]):
        self.RESOLUTER = resoluter

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

    def resolve(
        self, skirmish: Skirmish
    ) -> Tuple[Tuple[Civilization], Score, Score]:
        if skirmish.winner_ is not None:
            raise ValueError(ERR_MSG['already_resolved'])

        planet = skirmish.planet
        civilization_1 = skirmish.civilization_1
        civilization_2 = skirmish.civilization_2

        posture_1 = civilization_1.strategy(
            self=civilization_1, planet=planet, opponent=civilization_2)
        posture_2 = civilization_2.strategy(
            self=civilization_2, planet=planet, opponent=civilization_1)

        winner, score_1, score_2, result = self._decide_winner(
            posture_1, posture_2, civilization_1, civilization_2)
        skirmish.posture_1 = posture_1
        skirmish.posture_2 = posture_2
        skirmish.winner_ = winner
        skirmish.score_1 = score_1
        skirmish.score_2 = score_2
        skirmish.result = result

        return winner, score_1, score_2, result

    def _decide_winner(
        self,
        posture_1: Position,
        posture_2: Position,
        civilization_1: Civilization,
        civilization_2: Civilization
    ) -> Tuple[Tuple[Civilization], Score, Score, Result]:
        resoluter = self.RESOLUTER[(posture_1, posture_2,)]
        return resoluter(civilization_1, civilization_2)
