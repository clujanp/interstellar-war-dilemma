from ...base_model import CustomBaseModel
from .entities import Civilization, Skirmish


class Epoch(CustomBaseModel):
    index: int
    civilizations: tuple[Civilization, ...]
    skirmishes: list[Skirmish]
