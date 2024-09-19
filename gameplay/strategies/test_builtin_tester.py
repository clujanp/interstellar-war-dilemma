from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test_builtin_tester(memories, planet, opponent, resources):
    return BuiltInStrategies.tester(opponent=opponent, memories=memories)
