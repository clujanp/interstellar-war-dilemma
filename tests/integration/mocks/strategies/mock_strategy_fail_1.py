from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic,
    BuiltInStrategies
)


def test_fail1(
    opponent: Civilization, planet: Planet, memories: Memories, resources: int
) -> Position.COOPERATION | Position.AGGRESSION:
    return None
