from typing import List, Callable, Optional, Tuple, Dict
from collections import defaultdict
from app.core.domain.models import (
    Score, Result, Statistic, Civilization, Skirmish, Memories)


class MemoriesServiceWrapper:
    def __init__(self, memories: Memories = None, owner: Civilization = None):
        self._memories = memories or Memories(owner=owner)

    @property
    def owner(self) -> Civilization:
        return self._memories.owner

    @property
    def length(self) -> int:
        return len(self._memories.memories_)

    def remember(self, skirmish: Skirmish) -> None:
        self._memories.add(skirmish)

    def civilizations(self) -> List[Civilization]:
        return self._memories.civilizations

    def skirmishes_count(self, civilization: Civilization) -> int:
        return self._memories.skirmishes_count_by_civilization().get(
            civilization, 0)

    def last_position(self, civilization: Civilization) -> Optional[bool]:
        skirmish: List[Tuple[bool, Score]] = (
            self._memories.skirmishes_by_civilization().get(civilization, []))
        if not len(skirmish):
            return None
        return skirmish[-1][0]

    def last_score(
        self, civilization: Civilization
    ) -> Optional[Score.WIN | Score.LOSE | Score.TIE_GOOD | Score.TIE_BAD]:
        skirmish: List[Tuple[bool, Score]] = (
            self._memories.skirmishes_by_civilization().get(civilization, []))
        if not len(skirmish):
            return None
        return skirmish[-1][1]

    def cooperations(self, civilization: Civilization) -> Statistic:
        return self._statistics(civilization, Result.was_cooperative)

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

    def score(self, civilization: Civilization) -> int:
        return sum([
            score
            for posture, score in (
                self._memories.skirmishes_by_civilization()[civilization])
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

    def _statistics(
        self, civilization: Civilization, rule: Callable
    ) -> Statistic:
        return Statistic(sum([
            1 for posture, score in (
                self._memories.skirmishes_by_civilization().get(
                    civilization, [])
            ) if rule(posture, score)
        ]), total=self.skirmishes_count(civilization))
