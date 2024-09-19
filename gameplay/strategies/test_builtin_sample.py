from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test_builtin_sample(memories, planet, opponent, resources):
    return BuiltInStrategies.sample(opponent=opponent, memories=memories)
