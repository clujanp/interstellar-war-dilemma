from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic,
    BuiltInStrategies
)


def test_fail3(
    opponent: Civilization, planet: Planet, memories: Memories, resources: int
) -> Position.COOPERATION | Position.AGGRESSION:
    opponent.memory  # Fail protected by secure proxy
    return Position.COOPERATION
