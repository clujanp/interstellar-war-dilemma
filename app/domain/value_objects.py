from decimal import Decimal
from enum import StrEnum, IntEnum, Enum

class Resources(Decimal):
    """Represents Resources amount"""
    NONE: 'Resources'


Resources.NONE = Resources(0)


class Decision(IntEnum):
    """Represents a decision made by a player"""
    NOT_DECIDED = -1
    COOPERATE = 1
    DEFECT = 2


class Resolution(tuple, Enum):
    """Represents the resolution percentage of Resources gained
    by a civilization in a skirmish,
    based on Cooperation as 100% for both civilizations."""
    NOT_RESOLVED = (Decimal(0), Decimal(0))
    COOPERATION = (Decimal(3)/6, Decimal(3)/6)
    BETRAYAL_A = (Decimal(5)/6, Decimal(0))
    BETRAYAL_B = (Decimal(0), Decimal(5)/6)
    CONFLICT = (Decimal(1)/6, Decimal(1)/6)
    NOT_RESPONDED = (Decimal(1)/6, Decimal(1)/6)
    NOT_COOPERATE_A = (Decimal(1)/6, Decimal(2)/6)
    NOT_COOPERATE_B = (Decimal(2)/6, Decimal(1)/6)
    MASSACRE_A = (Decimal(5)/6, Decimal(0))
    MASSACRE_B = (Decimal(0), Decimal(5)/6)
    
    def __bool__(self):
        """A resolution is considered resolved if it's not NOT_RESOLVED."""
        return self != Resolution.NOT_RESOLVED


class AstronomicObjectType(StrEnum):
    """Represents an astronomical object classification"""
    PLANET = "planet"
    MOON = "moon"
    ASTEROID = "asteroid"
    ARTIFICIAL = "artificial"
