from decimal import Decimal
from enum import Enum, StrEnum, IntEnum
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class CivilizationStatus(StrEnum):
    ALIVE = "alive"
    DECLINING = "declining"
    DEAD = "dead"


class AstroKind(StrEnum):
    PLANET = "planet"
    STAR = "star"
    MOON = "moon"
    ASTEROID = "asteroid"
    ARTIFICIAL = "artificial"


class AstroBodyStatus(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    DESTROYED = "destroyed"


class Resources(Decimal):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, core_schema.decimal_schema())


class ColonizeCost(Resources, Enum):
    WITH_INFRAESTRUCTURE = Resources(0)
    TERRAFORMED = Resources(1)
    HABITABLE = Resources(2)
    NEED_TERRAFORM = Resources(3)
    HOSTILE = Resources(4)
    EXTREME = Resources(5)


class AstroBodyProduction(Resources, Enum):
    NULL = Resources(0)
    LOW = Resources(1)
    MEDIUM = Resources(2)
    HIGH = Resources(3)
    SUPERIOR = Resources(4)


class SkirmishStatus(StrEnum):
    ONGOING = "ongoing"
    FINISHED = "finished"


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


class Efficiency(Decimal, Enum):
    NONE = Decimal(0)
    CONFLICT = Decimal(0.17)
    COOPERATION = Decimal(0.5)
    MASSACRE = Decimal(0.66)
    TREASON = Decimal(0.83)
    ASSIMILATION = Decimal(0.92)
