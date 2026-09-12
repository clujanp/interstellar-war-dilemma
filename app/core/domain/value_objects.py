from enum import IntEnum


class Decision(IntEnum):
    COOPERATE = 1
    ATTACK = 2
    NONE = 0


class SkirmishResult(IntEnum):
    COOPERATION = 4
    TREASON_A = 7
    TREASON_B = 5
    CONFLICT = 8
    ASSIMILATION_A = 3
    ASSIMILATION_B = 1
    MASSACRE_A = 6
    MASSACRE_B = 2
    LOOSE = 0
