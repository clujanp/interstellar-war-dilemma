from pydantic import model_validator
from ..base_model import CustomBaseModel
from ..domain.models import Civilization, Skirmish
from ..domain.value_objects import Decision, SkirmishResult
from .dto import AstroBodyDTO
from .typing import StrategyCallable


class CivilizationRegistration(Civilization):
    callback: StrategyCallable

    @model_validator(mode="after")
    def validate_callback(self) -> "CivilizationRegistration":
        if not callable(self.callback):
            raise ValueError("callback must be callable")
        return self


class SkirmishRelated(CustomBaseModel):
    owner: CivilizationRegistration
    skirmish: Skirmish

    @model_validator(mode="after")
    def safe_port(self) -> "SkirmishRelated":
        if not isinstance(self.skirmish, Skirmish):
            raise ValueError("skirmish must be an instance of Skirmish")

        # pylint: disable=attribute-defined-outside-init
        self.__owner_index = self.skirmish.civilizations.index(self.owner)
        self.__opponent_index = 1 - self.__owner_index
        # pylint: disable=attribute-defined-outside-init
        self._opponent = (
            self.skirmish.civilizations[self.__opponent_index].name)
        self._astro = AstroBodyDTO(
            name=self.skirmish.astro_body.name,
            kind=self.skirmish.astro_body.kind,
            cost=self.skirmish.astro_body.colonize_cost,
            production=self.skirmish.astro_body.production,
        )
        return self

    # pylint: disable=multiple-statements
    @property
    def opponent(self) -> str:
        return self._opponent

    @property
    def astro(self) -> AstroBodyDTO:
        return self._astro

    @property
    def resources(self) -> float:
        return float(self.owner.resources)

    @property
    def decision(self) -> Decision:
        return getattr(self, "_decision", self.skirmish.decisions[
            self.__owner_index])

    @property
    def opponent_decision(self) -> Decision:
        return getattr(self, "_opponent_decision", self.skirmish.decisions[
            self.__opponent_index])

    @property
    def result(self) -> SkirmishResult:
        return getattr(self, "_result", self.skirmish.result)

    @property
    def gain_factor(self) -> float | None:
        return getattr(self, "_gain_factor", float(
            self.skirmish.production_participation[self.__owner_index]))
