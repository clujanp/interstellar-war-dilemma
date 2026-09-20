from random import choice
from pydantic import ConfigDict, model_validator
from ...base_model import CustomBaseModel
from ..value_objects import (
    CivilizationStatus, AstroKind, AstroBodyStatus, Efficiency, Resources,
    ColonizeCost, AstroBodyProduction, SkirmishResult, SkirmishStatus,
    Decision)


class Civilization(CustomBaseModel):
    name: str
    resources: Resources
    status: CivilizationStatus = CivilizationStatus.ALIVE

    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode="after")
    def update_resources(self) -> "Civilization":
        """Handle events related to the update of resources."""
        if self.resources <= 0 and self.status == CivilizationStatus.ALIVE:
            self.status = CivilizationStatus.DECLINING
        elif (
            self.resources > 0
            and self.status == CivilizationStatus.DECLINING
        ):
            self.status = CivilizationStatus.ALIVE
        return self


class AstroBody(CustomBaseModel):
    name: str
    kind: AstroKind
    colonize_cost: ColonizeCost
    production: AstroBodyProduction
    status: AstroBodyStatus = AstroBodyStatus.AVAILABLE

    @staticmethod
    def name_generator() -> str:
        """Generate a default name for the astro body."""
        prefix = [
            "Tan", "Remu", "Sirus", "Mal", "U", "Por", "Tie", "Vor", "Mor",
            "Gal", "Zen", "Xan", "Lun", "Cry", "Re", "Mar", "Sol", "Ven", "Ter"
        ]
        sufix = [
            "a", "o", "i", "tor", "us", "ra", "po", "li", "bucono", "zen",
            "quar", "mir", "thar", "vex", "zor", "lyn", "dra", "kel", "torin",
            "phar", "dor", "ach", "ion"
        ]
        return f"{choice(prefix)}{choice(sufix)}"


class Skirmish(CustomBaseModel):
    civilizations: tuple[Civilization, Civilization]
    astro_body: AstroBody
    decisions: list[Decision, Decision] = [Decision.NONE, Decision.NONE]
    result: None | SkirmishResult = None
    production_participation: tuple[Efficiency, Efficiency] = (
        Efficiency.NONE, Efficiency.NONE)
    status: SkirmishStatus = SkirmishStatus.ONGOING

    def resolve(self) -> SkirmishResult:
        """Resolve the skirmish based on the current decisions."""
        if self.status == SkirmishStatus.FINISHED:
            raise ValueError("Skirmish has already been resolved.")

        self.decisions = tuple(self.decisions)
        self.result = SkirmishResult(
            self.decisions[0] * len(Decision) + self.decisions[1])
        self._resolve_prodcution_parts()
        self.status = SkirmishStatus.FINISHED
        return self.result

    def _resolve_prodcution_parts(self) -> tuple[Efficiency, Efficiency]:
        """Resolve the production participation for each civilization."""
        if self.status == SkirmishStatus.FINISHED:
            return self.production_participation

        self.production_participation = {
            SkirmishResult.COOPERATION: (
                Efficiency.COOPERATION, Efficiency.COOPERATION,),
            SkirmishResult.TREASON_A: (Efficiency.TREASON, Efficiency.NONE,),
            SkirmishResult.TREASON_B: (Efficiency.NONE, Efficiency.TREASON,),
            SkirmishResult.CONFLICT: (
                Efficiency.CONFLICT, Efficiency.CONFLICT,),
            SkirmishResult.ASSIMILATION_A: (
                Efficiency.ASSIMILATION, Efficiency.NONE,),
            SkirmishResult.ASSIMILATION_B: (
                Efficiency.NONE, Efficiency.ASSIMILATION,),
            SkirmishResult.MASSACRE_A: (Efficiency.MASSACRE, Efficiency.NONE,),
            SkirmishResult.MASSACRE_B: (Efficiency.NONE, Efficiency.MASSACRE,),
            SkirmishResult.LOOSE: (Efficiency.NONE, Efficiency.NONE,),
        }[self.result]
        return self.production_participation
