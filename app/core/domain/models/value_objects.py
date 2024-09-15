class Score(int):
    LOSE = 0
    TIE_BAD = 1
    TIE_GOOD = 3
    WIN = 5
    MAX_SCORE = 6

    def __new__(cls, value: int):
        assert value in (cls.LOSE, cls.TIE_BAD, cls.TIE_GOOD, cls.WIN,), (
            "Invalid score value")
        return super().__new__(cls, value)

    def __str__(self): return super().__repr__()
    def __repr__(self): return f"<Score: {self}>"


class Cost:
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    NONE = 0


class Position:
    COOPERATION = True
    AGGRESSION = False
    FAIL = None  # fail in take a decision (raise an exception or return None)


class Result:
    COOPERATION = 1  # both cooperated
    CONQUEST = 0  # one cooperated and the other not
    AGGRESSION = -1  # both aggressed
    FAIL = -5  # both failed in take a decision

    was_cooperative = (  # noqa: E731
        lambda posture, score: posture is Position.COOPERATION)
    is_conquest = lambda posture, score: score == Score.WIN  # noqa: E731
    is_hit = (  # noqa: E731
        lambda posture, score: score in [Score.WIN, Score.TIE_GOOD])
    is_lose = (  # noqa: E731
        lambda posture, score: score in [Score.LOSE, Score.TIE_BAD])
    is_mistake = lambda posture, score: score == Score.LOSE  # noqa: E731
    is_failure = lambda posture, score: posture == Position.FAIL  # noqa: E731


class Statistic(int):
    def __new__(cls, value: int, total: int):
        assert value >= 0, "Invalid statistic value"
        value = super().__new__(cls, value)
        value.total = total
        return value

    def invert(self) -> 'Statistic':
        return Statistic(self.total - self, self.total)

    @property
    def percent(self) -> float:
        if self.total == 0:
            return 0.0
        return self / self.total

    def __str__(self): return super().__repr__()

    def __repr__(self):
        return f"<Statistic: {self.percent:.2f}>"
