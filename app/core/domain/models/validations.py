from pydantic import model_validator
from typing import Any
from typing_extensions import Self
from app.config.messages import ERR_MODELS_VALIDATIONS as ERR_MSG


class PlanetValidations:
    ...


class CivilizationValidations:
    ...


class SkirmishValidations:
    @model_validator(mode='before')
    @classmethod
    def validate_civilizations(cls, data: Any) -> Any:
        if data['civilization_1'] is data['civilization_2']:
            raise ValueError(ERR_MSG['civilizations_diff'])
        return data

    @model_validator(mode='after')
    def validate_planet(self) -> Self:
        if self.planet and self.civilization_1 and self.civilization_2:
            if self.planet.cost > min(
                self.civilization_1.resources, self.civilization_2.resources
            ):
                raise ValueError(ERR_MSG['not_enough_resources'])
            if self.planet.colonized:
                raise ValueError(ERR_MSG['planet_colonized'])

        return self


class MemoriesValidations:
    @model_validator(mode='after')
    def validate_owner_data(self) -> Self:
        from app.core.domain.models import Civilization, Planet

        AVAILABLE_KEYS_TYPES = (str,)
        AVAILABLE_VALUES_TYPES = (
            type(None), int, float, str, bool, Civilization, Planet,)

        if type(self.owner_data) is not dict:
            raise ValueError(ERR_MSG['owner_data_dict'])
        if len(self.owner_data) > 10:
            raise ValueError(ERR_MSG['owner_data_max_size'])
        for k, v in self.owner_data.items():
            if type(k) not in AVAILABLE_KEYS_TYPES:
                raise ValueError(ERR_MSG['owner_data_keys'])
            if type(v) not in AVAILABLE_VALUES_TYPES:
                raise ValueError(ERR_MSG['owner_data_values'])

        return self
