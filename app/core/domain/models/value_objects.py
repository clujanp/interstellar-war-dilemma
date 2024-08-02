class Score(int):
    LOSE = 0
    TIE_BAD = 1
    TIE_GOOD = 3
    WIN = 5
    COST_HIGH = 3
    COST_MEDIUM = 2
    COST_LOW = 1
    COST_NONE = 0

    def __new__(cls, value: int):
        assert value in (cls.LOSE, cls.TIE_BAD, cls.TIE_GOOD, cls.WIN,), (
            "Invalid score value")
        return super().__new__(cls, value)

    def __repr__(self): return str(self)


class Position:
    COOPERATION = True
    AGGRESSION = False


class Eval:
    was_cooperative = (  # noqa: E731
        lambda posture, score: posture is Position.COOPERATION)
    is_conquest = lambda posture, score: score == Score.WIN  # noqa: E731
    is_hit = (  # noqa: E731
        lambda posture, score: score in [Score.TIE_BAD, Score.TIE_GOOD])
    is_mistake = lambda posture, score: score == Score.LOSE  # noqa: E731


class Statistic(int):
    def __new__(cls, value: int, total: int):
        assert value >= 0, "Invalid statistic value"
        value = super().__new__(cls, value)
        value.total = total
        return value

    @property
    def percent(self) -> float:
        return self / 100
