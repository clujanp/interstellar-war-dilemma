from typing import Callable
from app.core.domain.models import Civilization
from .memories import MemoriesServiceWrapper


class CivilizationService:
    @classmethod
    def create(
        cls,
        name: str,
        strategy: Callable,
        resources: int,
    ) -> Civilization:
        civilization = Civilization(
            name=name,
            strategy=strategy,
            resources=resources,
        )
        civilization.memory.owner = civilization
        civilization.memory = MemoriesServiceWrapper(civilization.memory)
        return civilization
