from __future__ import annotations

from typing import Iterator

from app.domain.models import Match, Round, Civilization
from app.domain.services.round_context import RoundContext
from app.domain.value_objects import Resources
from app.interfaces.db import MatchRepository, RoundRepository


class MatchSession:
    """Manages the lifecycle of a match, coordinating rounds and persistence."""

    def __init__(
        self,
        civilizations: list[Civilization],
        target_rounds: int,
        match_repo: MatchRepository,
        round_repo: RoundRepository
    ) -> None:
        self._match_repo = match_repo
        self._round_repo = round_repo
        self._match = Match(
            target_rounds=target_rounds,
            civilizations=civilizations,
        )
        self._match.start()
        self._match_repo.save(self._match)

    @property
    def match(self) -> Match:
        """Access the current match."""
        return self._match

    def __iter__(self) -> Iterator[RoundContext]:
        """Iterate round by round until match completes or stops."""
        while self.match.can_start_round:
            self.match.advance_round()
            yield (round := RoundContext(
                civilizations=self.match.civilizations,
                match=self._match,
                round_repo=self._round_repo,
            ))
            self._update_scores(round.round)
                
        self.match.mark_completed()
        self._match_repo.save(self.match)

    def stop_match(self) -> Match:
        """Early stop the current match."""
        self.match.mark_stopped()
        self._match_repo.save(self.match)
        return self.match

    def _update_scores(self, round: Round) -> None:
        """Update cumulative scores from resolved skirmishes."""
        for skirmish in round.skirmishes:
            name_a = skirmish.civ_a.name
            name_b = skirmish.civ_b.name
            self.match.cumulative_scores[name_a] = Resources(
                self.match.cumulative_scores.get(name_a, Resources.NONE)
                + skirmish.civ_a_resources_gained
            )
            self.match.cumulative_scores[name_b] = Resources(
                self.match.cumulative_scores.get(name_b, Resources.NONE)
                + skirmish.civ_b_resources_gained
            )
