from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic,
    BuiltInStrategies
)


# No args fail
def test_fail2() -> Position.COOPERATION | Position.AGGRESSION:
    return None
