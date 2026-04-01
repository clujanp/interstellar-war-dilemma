from uuid import UUID

from app.domain.models import Skirmish
from app.interfaces.db import SkirmishQueryRepository


class MemoriesService:
    """Read-only query service for skirmish history. Reads from repository."""

    def __init__(self, skirmish_query_repo: SkirmishQueryRepository) -> None:
        self._repo = skirmish_query_repo

    def get_skirmish_history(
        self,
        owner_id: UUID,
        opponent_id: UUID | None = None,
        last_n: int | None = None,
    ) -> list[Skirmish]:
        """Query resolved skirmish history for a civilization."""
        return self._repo.get_by_player(
            owner_id=owner_id,
            opponent_id=opponent_id,
            last_n=last_n,
        )
