from app.domain.models import Civilization, Skirmish
from app.domain.exceptions import MemoriesValidationExcept


class Memories:
    """Class to store memories of past skirmishes and interactions."""
    def __init__(self, owner: Civilization):
        self.owner = owner
        self._skirmish_history: list[Skirmish] = []
        
    def record_skirmish(self, skirmish: Skirmish):
        """Record a skirmish in the memory."""
        if not skirmish.is_resolved:
            raise MemoriesValidationExcept(
                "Only resolved skirmishes can be recorded in memories.")
        if skirmish.civ_a != self.owner and skirmish.civ_b != self.owner:
            raise MemoriesValidationExcept(
                "Skirmish must involve the owner civilization.")
        self._skirmish_history.append(skirmish)
    
    def get_skirmish_history(
        self,
        opponent: Civilization | None = None,
        last_n: int | None = None,
    ) -> list[Skirmish]:
        """Get the history of skirmishes involving the owner civilization."""
        history = self._skirmish_history
        if opponent:
            history = [
                skirmish for skirmish in history
                if (skirmish.civ_a == opponent or skirmish.civ_b == opponent)
            ]
        if last_n is not None:
            if last_n < 0 or last_n > 1000:
                raise MemoriesValidationExcept(
                    "last_n must be between 0 and 1000.")
            if last_n == 0:
                return []
            history = history[-last_n:]

        # Return a shallow copy to avoid external mutation of internal state.
        return list(history)
        