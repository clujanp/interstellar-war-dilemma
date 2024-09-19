from app.core.domain.models import Position, Score, Result


RESOLUTER = {
    # k = Position 1, Position 2
    # v = lambda civ1, civ2: (winners, Score_1, Score_2, Result)
    (Position.COOPERATION, Position.COOPERATION,): lambda civ1, civ2: (
        (civ1, civ2,), Score.TIE_GOOD, Score.TIE_GOOD, Result.COOPERATION,),
    (Position.COOPERATION, Position.AGGRESSION,): lambda civ1, civ2: (
        (civ2,), Score.LOSE, Score.WIN, Result.CONQUEST,),
    (Position.AGGRESSION, Position.COOPERATION,): lambda civ1, civ2: (
        (civ1,), Score.WIN, Score.LOSE, Result.CONQUEST,),
    (Position.AGGRESSION, Position.AGGRESSION,): lambda civ1, civ2: (
        (civ1, civ2,), Score.TIE_BAD, Score.TIE_BAD, Result.AGGRESSION,),
    # fail cases
    (Position.FAIL, Position.COOPERATION,): lambda civ1, civ2: (
        (civ2,), Score.LOSE, Score.ALONE_WIN, Result.ALONE_WIN,),
    (Position.COOPERATION, Position.FAIL,): lambda civ1, civ2: (
        (civ1,), Score.ALONE_WIN, Score.LOSE, Result.ALONE_WIN,),
    (Position.FAIL, Position.AGGRESSION,): lambda civ1, civ2: (
        (civ2,), Score.LOSE, Score.WIN, Result.CONQUEST,),
    (Position.AGGRESSION, Position.FAIL,): lambda civ1, civ2: (
        (civ1,), Score.WIN, Score.LOSE, Result.CONQUEST,),
    (Position.FAIL, Position.FAIL,): lambda civ1, civ2: (
        tuple(), Score.LOSE, Score.LOSE, Result.FAIL,),
}


RESULT_EMOJI = {
    Result.COOPERATION: "🤝🏻",
    Result.CONQUEST: "🩸",
    Result.AGGRESSION: "⚔️ ",
    Result.ALONE_WIN: "😐",
    Result.FAIL: "🤡",
}


POSITION_EMOJI = {
    Position.COOPERATION: "✌🏻 ",
    Position.AGGRESSION: "🖕🏻",
    Position.FAIL: "🤷🏻",
}
