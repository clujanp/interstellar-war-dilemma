from . import (  # noqa: F401
    Civilization, Planet, Memories, Position, Statistic,
    BuiltInStrategies
)


def test_fail4(
    opponent: Civilization, planet: Planet, memories: Memories, resources: int
) -> Position.COOPERATION | Position.AGGRESSION:
    class MyHackedMemory:
        def __getattr__(self, name):
            return None
    opponent.memory = MyHackedMemory()  # Fail protected by secure proxy
    return Position.COOPERATION
