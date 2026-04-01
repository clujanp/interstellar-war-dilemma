from uuid import UUID, uuid4
from pydantic import (
    BaseModel as PyDanticBaseModel,
    Field,
    model_validator,
    ConfigDict,
    PrivateAttr,
)
from random import choice as random_choice
from .value_objects import (
    AstronomicObjectType, MatchStatus, Resources, Decision, Resolution)
from .exceptions import MatchValidationExcept, SkirmishResolvedExcept


class BaseModel(PyDanticBaseModel):
    """Base model for all domain models."""
    id: UUID = Field(default_factory=uuid4)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseModel):
            return NotImplemented
        return self.id == other.id


class Galaxy(BaseModel):
    """Group of star systems"""
    name: str
    type: str
    star_systems: list['StartSystem']
    
    
class StartSystem(BaseModel):
    """Group of astronomical objects orbiting a star"""
    name: str
    astronomical_objects: list['AstronomyBody']


class AstronomyBody(BaseModel):
    """Represents an astronomical object that disputes for resources"""
    name: str = Field(default_factory=lambda: AstronomyBody.generate_name())
    type: AstronomicObjectType
    resources: Resources
    owner: list['Civilization'] | None = None
        
    @staticmethod
    def generate_name() -> str:
        """Generate a random name for the astronomy body."""
        prefixes = [
            'Zor', 'Xan', 'Vel', 'Kry', 'Syn', 'Trant', 'Swi', 'Termin',
            'Nebul', 'Quar', 'Vort', 'Lun', 'Stell', 'Cosm', 'Galax', 'Orion',
        ]
        suffixes = [
            'on', 'or', 'ar', 'is', 'us', 'ia', 'or', 'ax', 'ena', 'ion',
            'ara', 'ix', 'a', 'e', 'i', 'o', 'u',
        ]
        return random_choice(prefixes) + random_choice(suffixes)
    
    
class Civilization(BaseModel):
    """Represents a civilization that competes for resources"""
    name: str
    home: AstronomyBody
    resources: Resources = Resources.NONE
    
    
# Gameplay models
class Match(BaseModel):
    """Aggregate root: represents a match simulation with n rounds."""
    status: MatchStatus = MatchStatus.PENDING
    target_rounds: int
    current_round: int = 0
    civilizations: list[Civilization] = Field(default_factory=list)
    cumulative_scores: dict[str, Resources] = Field(default_factory=dict)

    @property
    def can_start_round(self) -> bool:
        """Returns if a new round can be started."""
        return (
            self.status == MatchStatus.RUNNING
            and self.current_round < self.target_rounds
        )

    def start(self) -> None:
        """Transition from PENDING to RUNNING. Seed scores with home resources."""
        if self.status != MatchStatus.PENDING:
            raise MatchValidationExcept(
                "Match can only be started from PENDING status.")
        self.status = MatchStatus.RUNNING
        for civ in self.civilizations:
            self.cumulative_scores[civ.name] = civ.home.resources

    def advance_round(self) -> None:
        """Advance to the next round."""
        if not self.can_start_round:
            raise MatchValidationExcept(
                "Cannot advance round: match is not running "
                "or target rounds reached.")
        self.current_round += 1

    def mark_completed(self) -> None:
        """Transition from RUNNING to COMPLETED."""
        if self.status != MatchStatus.RUNNING:
            raise MatchValidationExcept(
                "Match can only be completed from RUNNING status.")
        self.status = MatchStatus.COMPLETED

    def mark_stopped(self) -> None:
        """Transition from RUNNING to STOPPED."""
        if self.status != MatchStatus.RUNNING:
            raise MatchValidationExcept(
                "Match can only be stopped from RUNNING status.")
        self.status = MatchStatus.STOPPED


class Round(BaseModel):
    """Represents a round of the game"""
    match: Match
    number: int
    skirmishes: list['Skirmish']


class Skirmish(BaseModel):
    """Represents a skirmish between two civilizations over an astro object"""
    civ_a: Civilization
    civ_b: Civilization
    astronomical_object: AstronomyBody
    resolution: Resolution = Resolution.NOT_RESOLVED
    decision_a: Decision | None = None
    decision_b: Decision | None = None
    civ_a_resources_gained: Resources = Resources.NONE
    civ_b_resources_gained: Resources = Resources.NONE
    _frozen: bool = PrivateAttr(default=False)

    def model_post_init(self, __context) -> None:
        # Keep skirmish immutable when loaded in a resolved state.
        self._frozen = bool(self.resolution)

    def __setattr__(self, name, value):
        if name in self.model_fields and self._frozen:
            raise SkirmishResolvedExcept("Skirmish is frozen after resolution.")
        super().__setattr__(name, value)
    
    @model_validator(mode='after')
    def validate_not_same_civilization(cls, skirmish) -> 'Skirmish':
        """Validates that both civilizations in the skirmish are different."""
        if skirmish.civ_a == skirmish.civ_b:
            raise ValueError(
                "Both civilizations in a skirmish must be different.")
        return skirmish

    def resolve(self):
        if not self.decision_a or not self.decision_b:
            raise SkirmishResolvedExcept(
                "Both civilizations must make a decision before resolving "
                "the skirmish."
            )
        if self.resolution:
            raise SkirmishResolvedExcept("Skirmish has already been resolved.")

        self._resolve_skirmish()
        self._calculate_gains()
        self._assign_owner_to_astronomical_object()
        self._frozen = True
        
    @property
    def is_resolved(self) -> bool:
        """Returns True if the skirmish has been resolved, False otherwise."""
        return bool(self.resolution)
        
    def _resolve_skirmish(self) -> None:
        """Resolves a skirmish based on the decisions of both civilizations."""
        match (self.decision_a, self.decision_b):
            case (Decision.COOPERATE, Decision.COOPERATE):
                self.resolution = Resolution.COOPERATION
            case (Decision.DEFECT, Decision.COOPERATE):
                self.resolution = Resolution.BETRAYAL_A
            case (Decision.COOPERATE, Decision.DEFECT):
                self.resolution = Resolution.BETRAYAL_B
            case (Decision.DEFECT, Decision.DEFECT):
                self.resolution = Resolution.CONFLICT
            case (Decision.NOT_DECIDED, Decision.NOT_DECIDED):
                self.resolution = Resolution.NOT_RESPONDED
            case (Decision.NOT_DECIDED, Decision.COOPERATE):
                self.resolution = Resolution.NOT_COOPERATE_A
            case (Decision.COOPERATE, Decision.NOT_DECIDED):
                self.resolution = Resolution.NOT_COOPERATE_B
            case (Decision.NOT_DECIDED, Decision.DEFECT):
                self.resolution = Resolution.MASSACRE_A
            case (Decision.DEFECT, Decision.NOT_DECIDED):
                self.resolution = Resolution.MASSACRE_B
        
    def _calculate_gains(self) -> None:
        """Calculates the resources gained by each civilization based on the
        resolution of the skirmish."""
        self.civ_a_resources_gained = Resources(
            self.astronomical_object.resources * self.resolution.value[0])
        self.civ_b_resources_gained = Resources(
            self.astronomical_object.resources * self.resolution.value[1])
        
    def _assign_owner_to_astronomical_object(self) -> None:
        """Assigns the owner of the astronomical object based on the resources
        gained by each civilization."""
        if self.civ_a_resources_gained > self.civ_b_resources_gained:
            self.astronomical_object.owner = [self.civ_a]
        elif self.civ_b_resources_gained > self.civ_a_resources_gained:
            self.astronomical_object.owner = [self.civ_b]
        else:
            self.astronomical_object.owner = [self.civ_a, self.civ_b]
