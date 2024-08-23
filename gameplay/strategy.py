from random import choice
from app.core.domain.models import Civilization, Planet, Position


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
    def reply_last(
        self: Civilization, opponent: Civilization, **_
    ) -> bool:
        last_skirmish = self.memory.last_position(opponent)
        if last_skirmish is not None:
            return last_skirmish
        return choice([Position.COOPERATION, Position.AGGRESSION])
