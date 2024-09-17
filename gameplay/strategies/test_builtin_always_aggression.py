from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test_builtin_always_cooperation(memories, planet, opponent, resources):
    return BuiltInStrategies.always_cooperation()
