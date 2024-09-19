from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test_builtin_friedman(memories, planet, opponent, resources):
    return BuiltInStrategies.friedman(opponent=opponent, memories=memories)
