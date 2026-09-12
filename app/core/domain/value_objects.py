from enum import Enum


class Desicion(int):
    ...


class SkirmishDecision(Desicion, Enum):
    COOPERATE = 1
    ATTACK = 2
    NONE = 0
