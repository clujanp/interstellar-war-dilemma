from typing import Literal
from pydantic import BaseModel
from ..domain.value_objects import Decision, SkirmishResult
from .typing import URIAppHttps


class RegistrationDTO(BaseModel):
    name: str
    callback_uri: URIAppHttps


class AstroBodyDTO(BaseModel):
    name: str
    kind: str
    cost: float
    production: float


class SkirmishDTO(BaseModel):
    opponent: str
    astro: AstroBodyDTO
    decision: Decision
    opponent_decision: Decision
    result: SkirmishResult
    gain_factor: float


class StrategyResponseDto(BaseModel):
    decision: Literal[
        "COOPERATE",
        "ATTACK",
        "NONE",
    ]
