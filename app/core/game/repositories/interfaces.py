from abc import ABC, abstractmethod
from ulid import ULID
from ...domain.value_objects import Decision
from ...domain.models import AstroBody
from ..models import CivilizationRegistration, SkirmishRelated
from ..dto import AstroBodyDTO
from ..typing import URIAppHttps


class IPlayersRepo(ABC):
    """Interface for players repository."""

    @abstractmethod
    def register_player(self, player_registration: CivilizationRegistration) -> None:
        """Registers a player in the repository."""

    @abstractmethod
    def unregister_player(self, player_id: ULID) -> None:
        """Unregisters a player from the repository using their ID."""

    @abstractmethod
    def get_player(self, player_id: ULID) -> CivilizationRegistration | None:
        """Retrieves a player's registration by their ID."""

    @abstractmethod
    def list_players(self) -> list[CivilizationRegistration]:
        """Lists all registered players."""


class IStrategiesRepo(ABC):
    """Interface for strategies repository."""

    @abstractmethod
    def register(self, callback_uri: URIAppHttps, name: str) -> IStrategy:
        """Registers a strategy using the provided callback URI."""

    @abstractmethod
    def unregister(self, callback_uri: URIAppHttps, name: str) -> None:
        """Unregisters a strategy using the provided callback URI."""

    @abstractmethod
    def get(self, callback_uri: URIAppHttps, name: str) -> IStrategy | None:
        """Retrieves a strategy by its callback URI."""

    @abstractmethod
    def list(self) -> list[IStrategy]:
        """Lists all registered strategies."""


class IStrategy(ABC):
    """Interface for a strategy."""

    @abstractmethod
    def __call__(
        self,
        opponent: str,
        astro: AstroBodyDTO,
        resources: float,
    ) -> Decision:
        """Executes the strategy and returns a decision."""


class ISkirmishesRepo(ABC):
    """Interface for skirmishes repository."""

    @abstractmethod
    def record(self, skirmish: SkirmishRelated) -> None:
        """Records a skirmish in the repository."""

    @abstractmethod
    def list(self) -> list[SkirmishRelated]:
        """Lists all recorded skirmishes."""

    @abstractmethod
    def query(
        self,
        owner: CivilizationRegistration,
        opponent: str | None = None,
        last: int = 100,
    ) -> list[SkirmishRelated]:
        """Queries the skirmishes given filters."""

    @abstractmethod
    def get_all_astro_bodies(self) -> set[AstroBody]:
        """Retrieves all astro bodies involved in skirmishes."""
