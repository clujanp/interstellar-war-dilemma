from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic,
    BuiltInStrategies
)


def test01(
    opponent: Civilization, planet: Planet, memories: Memories, resources: int
) -> Position.COOPERATION | Position.AGGRESSION:
    opponent_aggression_stats: Statistic = memories.aggressions(opponent)
    percent = opponent_aggression_stats.percent
    if percent > 0.91:
        return False
    return True
