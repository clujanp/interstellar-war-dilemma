from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, BuiltInStrategies)


def test01(
    opponent: Civilization, planet: Planet, memories: Memories, resources: int
) -> Position.COOPERATION | Position.AGGRESSION:
    aggre_sta = memories.aggressions(opponent)
    percent = aggre_sta.percent
    if percent > 0.91:
        return False
    return True
