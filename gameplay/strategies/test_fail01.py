from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic, Cost, Score,
    BuiltInStrategies
)
import logging


def test_80_timebomb(memories, planet, opponent, resources):
    if memories.length >= 2:
        logging.warn('Timebomb')
        return None
    return BuiltInStrategies.random()
