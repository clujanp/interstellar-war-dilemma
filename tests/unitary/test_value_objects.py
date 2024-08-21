import init  # noqa: F401
from unittest import TestCase
from app.core.domain.models.value_objects import (
    Score, Position, Result, Statistic)


class TestScore(TestCase):
    def test_score_creation_success(self):
        score = Score(Score.WIN)
        assert score == Score.WIN

    def test_score_creation_fail(self):
        with self.assertRaises(AssertionError):
            Score(10)


class TestPosition(TestCase):
    def test_position_constants(self):
        assert Position.COOPERATION is True
        assert Position.AGGRESSION is False


class TestResult(TestCase):
    def setUp(self):
        self.positions = [Position.COOPERATION, Position.AGGRESSION]
        self.scores = [Score.LOSE, Score.TIE_BAD, Score.TIE_GOOD, Score.WIN]

    def test_was_cooperative(self):
        for posture in self.positions:
            for score in self.scores:
                result = Result.was_cooperative(posture, score)
                if posture is Position.COOPERATION:
                    assert result is True
                else:
                    assert result is False

    def test_is_conquest(self):
        for posture in self.positions:
            for score in self.scores:
                result = Result.is_conquest(posture, score)
                if score in [Score.WIN]:
                    assert result is True
                else:
                    assert result is False

    def test_is_hit(self):
        for posture in self.positions:
            for score in self.scores:
                result = Result.is_hit(posture, score)
                if score in [Score.WIN, Score.TIE_GOOD]:
                    assert result is True
                else:
                    assert result is False

    def test_is_lose(self):
        for posture in self.positions:
            for score in self.scores:
                result = Result.is_lose(posture, score)
                if score in [Score.LOSE, Score.TIE_BAD]:
                    assert result is True
                else:
                    assert result is False

    def test_is_mistake(self):
        for posture in self.positions:
            for score in self.scores:
                result = Result.is_mistake(posture, score)
                if score in [Score.LOSE]:
                    assert result is True
                else:
                    assert result is False


class TestStatistic(TestCase):
    def test_statistic_creation_success(self):
        stat = Statistic(50, 100)
        assert stat == 50
        assert stat.total == 100

    def test_statistic_creation_fail(self):
        with self.assertRaises(AssertionError):
            Statistic(-1, 100)

    def test_statistic_percent(self):
        assert Statistic(50, 100).percent == 0.5  # NOSONAR: S1244
        assert Statistic(2, 20).percent == 0.1  # NOSONAR: S1244

    def test_statistic_invert(self):
        stat = Statistic(50, 100)
        invert = stat.invert()
        assert invert == 50
        assert invert.total == 100
        assert invert.percent == 0.5  # NOSONAR: S1244
