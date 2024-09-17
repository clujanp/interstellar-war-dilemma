from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)


def test_builtin_tic_for_tac(memories, planet, opponent, resources):
    return BuiltInStrategies.tic_for_tac(opponent=opponent, memories=memories)
