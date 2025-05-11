from enum import IntEnum


class Score(IntEnum):
    LOSE = 0
    TIE_BAD = 1
    ALONE_WIN = 2
    TIE_GOOD = 3
    WIN = 5
    MAX_SCORE = 6


class Cost(IntEnum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    NONE = 0


class Position:
    COOPERATION = True
    AGGRESSION = False
    FAIL = None  # fail in take a decision (raise an exception or return None)
    VALID_RESPONSE = [COOPERATION, AGGRESSION]
    ALL = [COOPERATION, AGGRESSION, FAIL]


class Result:
    COOPERATION = 'coo'  # both cooperated
    CONQUEST = 0  # one cooperated and the other not
    AGGRESSION = -3  # both aggressed
    ALONE_WIN = -3  # one cooperated and the other failed
    FAIL = -5  # both failed in take a decision

    TO_VALUE = {
        COOPERATION: 0,
        CONQUEST: 0,
        AGGRESSION: -3,
        ALONE_WIN: -3,
        FAIL: -5,
    }

    was_cooperative = (  # noqa: E731
        lambda posture, _: posture == Position.COOPERATION)
    was_aggresive = (   # noqa: E731
        lambda posture, _: posture == Position.AGGRESSION)
    was_fail = lambda posture, _: posture == Position.FAIL  # noqa: E731
    is_conquest = lambda _, score: score == Score.WIN  # noqa: E731
    is_hit = (  # noqa: E731
        lambda _, score: score in [Score.WIN, Score.TIE_GOOD])
    is_lose = (  # noqa: E731
        lambda _, score: score in [Score.LOSE, Score.TIE_BAD])
    is_mistake = lambda _, score: score == Score.LOSE  # noqa: E731


class Statistic(int):
    def __new__(cls, value: int, total: int):
        assert value >= 0, "Invalid statistic value"
        obj = super().__new__(cls, value)
        obj.total = total
        return obj

    def invert(self) -> 'Statistic':
        return Statistic(self.total - self, self.total)

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 0.0
        return self / self.total

    def __hash__(self): return hash(self.percent)
    def __str__(self): return super().__repr__()
    def __repr__(self): return f"<Statistic: {self.percent:.2f}>"
