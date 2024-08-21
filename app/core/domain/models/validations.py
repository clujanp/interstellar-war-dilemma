from pydantic import model_validator
from typing import Any
from typing_extensions import Self


class PlanetValidations:
    ...


class CivilizationValidations:
    ...


class SkirmishValidations:
    @model_validator(mode='before')
    @classmethod
    def validate_civilizations(cls, data: Any) -> Any:
        if data['civilization_1'] is data['civilization_2']:
            raise ValueError("Civilizations must be different")
        return data

    @model_validator(mode='after')
    def validate_planet(self) -> Self:
        if self.planet and self.civilization_1 and self.civilization_2:
            if self.planet.cost > min(
                self.civilization_1.resources, self.civilization_2.resources
            ):
                raise ValueError("Not enough resources to colonize the planet")
            if self.planet.colonized:
                raise ValueError("Planet already colonized")

        return self


class MemoriesValidations:
    ...
