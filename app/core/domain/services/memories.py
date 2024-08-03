from typing import List, Callable
from app.core.domain.models import Eval, Statistic, Civilization, Memories


class MemoriesService:
    @classmethod
    def civilizations(cls, memories: Memories) -> List[Civilization]:
        return memories.civilizations()

    @classmethod
    def cooperations(
        cls, memories: Memories, civilization: Civilization
    ) -> Statistic:
        return cls._statistics(memories, civilization, Eval.was_cooperative)

    @classmethod
    def aggressions(
        cls, memories: Memories, civilization: Civilization
    ) -> Statistic:
        return cls.cooperations(memories, civilization).invert()

    @classmethod
    def conquests(
        cls, memories: Memories, civilization: Civilization
    ) -> Statistic:
        return cls._statistics(memories, civilization, Eval.is_conquest)

    @classmethod
    def hits(
        cls, memories: Memories, civilization: Civilization
    ) -> Statistic:
        return cls._statistics(memories, civilization, Eval.is_hit)

    @classmethod
    def mistakes(
        cls, memories: Memories, civilization: Civilization
    ) -> Statistic:
        return cls._statistics(memories, civilization, Eval.is_mistake)

    @staticmethod
    def _statistics(
        memories: Memories, civilization: Civilization, rule: Callable
    ) -> Statistic:
        return Statistic(sum([
            1 for posture, score in memories.skirmishes()[civilization]
            if rule(posture, score)
        ]), total=len(memories.memories_))
