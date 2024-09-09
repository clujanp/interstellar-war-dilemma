from random import choice, random
from .classes import Civilization, Memories, Position
from app.infraestructure.logging import logger


class BuiltInStrategies:
    """A collection of built-in strategies that can be used in the game."""

    @staticmethod
    def always_cooperation(**_) -> bool:
        return Position.COOPERATION

    @staticmethod
    def always_aggression(**_) -> bool:
        return Position.AGGRESSION

    @staticmethod
    def random(**_) -> bool:
        return choice([Position.COOPERATION, Position.AGGRESSION])

    @staticmethod
    def tic_for_tac(
        opponent: Civilization, memories: Memories, **_
    ) -> bool:
        last_position = memories.last_position(opponent)
        if last_position is not None:
            return last_position
        return Position.COOPERATION

    @staticmethod
    def friedman(
        opponent: Civilization, memories: Memories, **_
    ) -> bool:
        aggressions = memories.aggressions(opponent)
        print(f"{aggressions.percent = }")
        if aggressions.percent > 0:
            return Position.AGGRESSION
        return Position.COOPERATION

    @staticmethod
    def joss(opponent: Civilization, memories: Memories, **_) -> bool:
        if random() < 0.10:
            return Position.AGGRESSION
        last_position = memories.last_position(opponent)
        if last_position is not None:
            return last_position
        return Position.COOPERATION

    @staticmethod
    def sample(opponent: Civilization, memories: Memories, **_) -> bool:
        if memories.skirmishes_count(opponent) >= 2:
            last_positions = memories.last_position(opponent, 2)
            if last_positions == [Position.AGGRESSION, Position.AGGRESSION]:
                return Position.AGGRESSION
            return Position.COOPERATION
        return Position.COOPERATION

    @staticmethod
    def tester(opponent: Civilization, memories: Memories, **_) -> bool:
        count_skirmishes = memories.skirmishes_count(opponent)
        if count_skirmishes == 1:
            return Position.AGGRESSION
        if count_skirmishes >= 2:
            if memories.first_position(opponent, 2)[1] == Position.AGGRESSION:
                return memories.last_position(opponent)
            if count_skirmishes % 2 == 0:
                return Position.AGGRESSION
            else:
                return Position.COOPERATION
        return Position.COOPERATION


def config(**configs: dict) -> callable:
    AVAILABLE_CONFIGS = {
        'allies': list
    }

    assert all(config in AVAILABLE_CONFIGS for config in configs), (
        f"Invalid config: {configs}, must be one of {AVAILABLE_CONFIGS}")
    for config, value in configs.items():
        assert isinstance(value, AVAILABLE_CONFIGS[config]), (
            f"Invalid value for {config}, must be {AVAILABLE_CONFIGS[config]}")

    def decorator(strategy: callable) -> callable:
        setattr(strategy, 'config', configs)
        return strategy
    return decorator
