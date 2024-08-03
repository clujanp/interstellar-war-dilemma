import init  # noqa: F401
from unittest import TestCase
from app.core.domain.models.value_objects import (
    Score, Position, Eval, Statistic)


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


class TestEval(TestCase):
    def setUp(self):
        self.posture_cooperation = Position.COOPERATION
        self.posture_aggression = Position.AGGRESSION

    def test_was_cooperative_success(self):
        result = Eval.was_cooperative(self.posture_cooperation, Score.WIN)
        assert result is True

    def test_was_cooperative_fail(self):
        result = Eval.was_cooperative(self.posture_aggression, Score.WIN)
        assert result is False

    def test_is_conquest_success(self):
        result = Eval.is_conquest(self.posture_cooperation, Score.WIN)
        assert result is True

    def test_is_conquest_fail(self):
        result = Eval.is_conquest(self.posture_cooperation, Score.LOSE)
        assert result is False

    def test_is_hit_success(self):
        result = Eval.is_hit(self.posture_cooperation, Score.TIE_BAD)
        assert result is True

    def test_is_hit_fail(self):
        result = Eval.is_hit(self.posture_cooperation, Score.LOSE)
        assert result is False

    def test_is_mistake_success(self):
        result = Eval.is_mistake(self.posture_cooperation, Score.LOSE)
        assert result is True

    def test_is_mistake_fail(self):
        result = Eval.is_mistake(self.posture_cooperation, Score.WIN)
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
        stat = Statistic(50, 100)
        assert stat.percent == 0.5  # NOSONAR: S1244

    def test_statistic_invert(self):
        stat = Statistic(50, 100)
        invert = stat.invert()
        assert invert == 50
        assert invert.total == 100
        assert invert.percent == 0.5  # NOSONAR: S1244
