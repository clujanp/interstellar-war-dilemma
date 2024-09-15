from typing import List, Callable, Optional, Tuple, Dict
from app.core.domain.models import (
    Score, Result, Statistic, Planet, Civilization, Skirmish, Memories)


class MemoriesServiceWrapper:
    def __init__(self, memories: Memories = None, owner: Civilization = None):
        self._memories = memories or Memories(owner=owner)

    @property
    def owner(self) -> Civilization:
        return self._memories.owner

    @property
    def length(self) -> int:
        return len(self._memories.memories_)

    @property
    def own_info(self) -> Dict[
        str, Optional[Planet | Civilization | str | int | float | bool]
    ]:
        return self._memories.owner_data

    @own_info.setter
    def own_info(
        self, data: Dict[
            str, Optional[Planet | Civilization | str | int | float | bool]]
    ) -> None:
        AVAILABLE_VALUES_TYPES = (
            type(None), int, float, str, bool, Civilization, Planet,)
        for k, v in data.items():
            print(f"{k = }, {v = } {type(v) = } {v.__class__ = }")
        self._memories.owner_data = {
            k: v for k, v in data.items()
            if type(v) in AVAILABLE_VALUES_TYPES
        }

    def remember(self, skirmish: Skirmish) -> None:
        self._memories.add(skirmish)

    def civilizations(self) -> List[Civilization]:
        return self._memories.civilizations

    def skirmishes_count(self, civilization: Civilization) -> int:
        return self._memories.skirmishes_count_by_civilization().get(
            civilization, 0)

    def first_positions(
        self, civilization: Civilization, n: int = 1
    ) -> List[bool]:
        return self._get_position_or_score(
            civilization, n, score_instead_position=False)

    def first_scores(
        self, civilization: Civilization, n: int = 1
    ) -> List[Score]:
        return self._get_position_or_score(
            civilization, n, score_instead_position=True)

    def last_positions(
        self, civilization: Civilization, n: int = 1
    ) -> List[bool]:
        return self._get_position_or_score(
            civilization, n, score_instead_position=False, reverse=True)

    def last_scores(
        self, civilization: Civilization, n: int = 1
    ) -> List[Score]:
        return self._get_position_or_score(
            civilization, n, score_instead_position=True, reverse=True)

    def cooperations(self, civilization: Civilization) -> Statistic:
        _return = self._statistics(civilization, Result.was_cooperative)
        import logging
        logging.debug(f"{type(_return) = } {_return = }")
        return _return

    def aggressions(self, civilization: Civilization) -> Statistic:
        return self.cooperations(civilization).invert()

    def conquests(self, civilization: Civilization) -> Statistic:
        return self._statistics(civilization, Result.is_conquest)

    def hits(self, civilization: Civilization) -> Statistic:
        return self._statistics(civilization, Result.is_hit)

    def loss(self, civilization: Civilization) -> Statistic:
        return self._statistics(civilization, Result.is_lose)

    def mistakes(self, civilization: Civilization) -> Statistic:
        return self._statistics(civilization, Result.is_mistake)

    def fails(self, civilization: Civilization) -> Statistic:
        return self._statistics(civilization, Result.is_failure)

    def score(self, civilization: Civilization) -> int:
        return sum([
            score
            for posture, score in self._skirmishes(civilization)
        ])

    def save(self) -> None:
        ...

    def summary(self) -> Dict[Civilization, Dict[str, int]]:
        from collections import OrderedDict

        civilizations_score = {}
        for civilization in self.civilizations():
            civilizations_score[civilization] = {
                'score': self.score(civilization),
                'accuracy': self.hits(civilization).percent,
                'position': self.cooperations(civilization).percent,
            }
        civilizations_score = OrderedDict(sorted(
            civilizations_score.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        ))
        return civilizations_score

    def report(self) -> Dict[str, Dict[str, int]]:
        resolutions = {'cooperations': 0, 'conquests': 0, 'aggressions': 0}
        for skirmish in self._memories.skirmishes:
            result = skirmish.result
            if result == Result.COOPERATION:
                key = 'cooperations'
            elif result == Result.CONQUEST:
                key = 'conquests'
            else:
                key = 'aggressions'
            resolutions[key] += 1

        report = {
            'skirmishes': self.length,
            'max_score_reachable': Score.MAX_SCORE * self.length,
            'score_reached': sum([
                skirmish.combined_score
                for skirmish in self._memories.skirmishes
            ]),
            'resolutions': resolutions,
            'avg_planets_cost': sum([
                skirmish.planet.cost
                for skirmish in self._memories.skirmishes
            ]) / self.length,
        }

        return report

    def _get_position_or_score(
        self,
        civilization: Civilization,
        last: int = 1,
        score_instead_position: bool = True,
        reverse: bool = False,
    ) -> List[Score | bool]:
        assert last > 0
        skirmishes: List[Tuple[bool, Score]] = self._skirmishes(civilization)
        if reverse:
            skirmishes.reverse()
        return [
            skirmish[int(score_instead_position)]
            for skirmish in skirmishes[:last]
        ]

    def _skirmishes(
        self, civilization: Civilization
    ) -> List[Tuple[bool, Score]]:
        return self._memories.skirmishes_by_civilization().get(
            civilization, [])

    def _statistics(
        self, civilization: Civilization, rule: Callable
    ) -> Statistic:
        return Statistic(sum([
            1 for posture, score in self._skirmishes(civilization)
            if rule(posture, score)
        ]), total=self.skirmishes_count(civilization))
