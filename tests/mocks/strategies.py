# pylint: disable=unused-argument
from contextlib import contextmanager
from random import choice
from typing import Generator
from app.core.game.repositories.wrappers import StrategyLocal
from app.core.game.models import Decision, AstroBodyDTO


@contextmanager
def fixture_local_random() -> Generator[StrategyLocal, None, None]:
    try:
        @StrategyLocal.register
        def random(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return choice([Decision.ATTACK, Decision.COOPERATE])

        yield random
    finally:
        StrategyLocal.unregister(random)


@contextmanager
def fixture_local_strategies() -> Generator[
    tuple[StrategyLocal, StrategyLocal, StrategyLocal], None, None
]:
    try:
        @StrategyLocal.register
        def all_out_attack(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.ATTACK

        @StrategyLocal.register
        def all_out_cooperate(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.COOPERATE

        @StrategyLocal.register
        def all_out_neutral(
            opponent: str, astro: AstroBodyDTO, resources: float
        ) -> Decision:
            return Decision.NONE

        yield all_out_attack, all_out_cooperate, all_out_neutral
    finally:
        StrategyLocal.unregister(all_out_attack)
        StrategyLocal.unregister(all_out_cooperate)
        StrategyLocal.unregister(all_out_neutral)
