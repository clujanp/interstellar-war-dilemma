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
        from random import choice
        return choice([Position.COOPERATION, Position.AGGRESSION])

    @staticmethod
    def reply_last(
        self: Civilization, opponent: Civilization, **_
    ) -> bool:
        from random import choice
        last_skirmish = self.memory.last_position(opponent)
        if last_skirmish is not None:
            return last_skirmish
        return choice([Position.COOPERATION, Position.AGGRESSION])


AVAILABLE_STRATEGIES = {
    'always_cooperation': BuiltInStrategies.always_cooperation,
    'always_aggression': BuiltInStrategies.always_aggression,
    'random': BuiltInStrategies.random,
    'reply_last': BuiltInStrategies.reply_last,
}


def select_random_builtin() -> callable:
    return choice(list(AVAILABLE_STRATEGIES.values()))
