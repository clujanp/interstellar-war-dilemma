from random import choice, random
from .classes import Civilization, Memories, Position


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
        return choice(Position.VALID_RESPONSE)

    @staticmethod
    def tic_for_tac(
        opponent: Civilization, memories: Memories, **_
    ) -> bool:
        last_positions = memories.last_positions(opponent)
        if last_positions and last_positions[0] is not Position.FAIL:
            return last_positions[0]
        return Position.COOPERATION

    @staticmethod
    def friedman(
        opponent: Civilization, memories: Memories, **_
    ) -> bool:
        aggressions = memories.aggressions(opponent)
        if aggressions.percent > 0:
            return Position.AGGRESSION
        return Position.COOPERATION

    @staticmethod
    def joss(opponent: Civilization, memories: Memories, **_) -> bool:
        if random() < 0.10:
            return Position.AGGRESSION
        last_positions = memories.last_positions(opponent)
        if last_positions and last_positions[0] is not Position.FAIL:
            return last_positions[0]
        return Position.COOPERATION

    @staticmethod
    def sample(opponent: Civilization, memories: Memories, **_) -> bool:
        if memories.skirmishes_count(opponent) >= 2:
            last_positions = memories.last_positions(opponent, 2)
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
            if memories.first_positions(opponent, 2)[1] == Position.AGGRESSION:
                return memories.last_positions(opponent)[0]
            if count_skirmishes % 2 == 0:
                return Position.AGGRESSION
            else:
                return Position.COOPERATION
        return Position.COOPERATION
