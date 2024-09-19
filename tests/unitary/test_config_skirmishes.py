import init  # noqa: F401
from unittest import TestCase
from app.config.skirmishes import RESOLUTER, RESULT_EMOJI, POSITION_EMOJI
from app.core.domain.models import Position, Score, Result


class TestConfigSkirmishes(TestCase):
    def setUp(self):
        self.civ1 = "TestCiv1"
        self.civ2 = "TestCiv2"

    def test_resoluter_success(self):
        civ1 = self.civ1
        civ2 = self.civ2
        WIN = Score.WIN
        LOSE = Score.LOSE
        TIE_GOOD = Score.TIE_GOOD
        TIE_BAD = Score.TIE_BAD
        ALONE = Score.ALONE_WIN
        COO = Position.COOPERATION
        AGR = Position.AGGRESSION
        FAIL = Position.FAIL
        R_COO = Result.COOPERATION
        R_CON = Result.CONQUEST
        R_AGR = Result.AGGRESSION
        R_ALONE = Result.ALONE_WIN
        R_FAIL = Result.FAIL

        assert (
            (civ1, civ2,), TIE_GOOD, TIE_GOOD, R_COO) == RESOLUTER.get(
            (COO, COO,))(civ1, civ2)
        assert ((civ1, civ2,), TIE_BAD, TIE_BAD, R_AGR) == RESOLUTER.get(
            (AGR, AGR,))(civ1, civ2)
        assert ((civ2,), LOSE, WIN, R_CON) == RESOLUTER.get(
            (COO, AGR,))(civ1, civ2)
        assert ((civ1,), WIN, LOSE, R_CON) == RESOLUTER.get(
            (AGR, COO,))(civ1, civ2)
        # fail cases
        assert ((civ2,), LOSE, ALONE, R_ALONE) == RESOLUTER.get(
            (FAIL, COO,))(civ1, civ2)
        assert ((civ1,), ALONE, LOSE, R_ALONE) == RESOLUTER.get(
            (COO, FAIL,))(civ1, civ2)
        assert ((civ2,), LOSE, WIN, R_CON) == RESOLUTER.get(
            (FAIL, AGR,))(civ1, civ2)
        assert ((civ1,), WIN, LOSE, R_CON) == RESOLUTER.get(
            (AGR, FAIL,))(civ1, civ2)
        assert (tuple(), LOSE, LOSE, R_FAIL) == RESOLUTER.get(
            (FAIL, FAIL,))(civ1, civ2)

    def test_result_emoji_success(self):
        assert "🤝🏻" == RESULT_EMOJI[Result.COOPERATION]
        assert "🩸" == RESULT_EMOJI[Result.CONQUEST]
        assert "⚔️ " == RESULT_EMOJI[Result.AGGRESSION]
        assert "😐" == RESULT_EMOJI[Result.ALONE_WIN]
        assert "🤡" == RESULT_EMOJI[Result.FAIL]

    def test_position_emoji_success(self):
        assert "✌🏻 " == POSITION_EMOJI[Position.COOPERATION]
        assert "🖕🏻" == POSITION_EMOJI[Position.AGGRESSION]
        assert "🤷🏻" == POSITION_EMOJI[Position.FAIL]
