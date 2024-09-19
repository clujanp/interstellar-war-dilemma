from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test_builtin_joss(memories, planet, opponent, resources):
    return BuiltInStrategies.joss(opponent=opponent, memories=memories)
