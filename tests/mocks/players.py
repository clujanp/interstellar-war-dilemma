from itertools import cycle
from contextlib import contextmanager
from typing import Generator
from app.core.game.dto import RegistrationDTO
from app.core.game.services.flow import GameFlow
from app.core.game.typing import URIAppHttps


def generator_registration(
    n: int,
    custom_callback: tuple[URIAppHttps, ...],
) -> list[RegistrationDTO]:
    # call callables items in custom_callback
    custom_callbacks = cycle(custom_callback)
    return [RegistrationDTO(
        name=f"Player{i}",
        callback_uri=next(custom_callbacks),
    ) for i in range(n)]


@contextmanager
def setup_player_registration(
    flow_service: GameFlow,
    registrations: RegistrationDTO,
    init_resources: float = 100.0,
) -> Generator[None, None, None]:
    """Setup player in flow service"""
    try:
        civ_registrations = []
        for registration in registrations:
            civ_registrations.append(flow_service.civilization_registration(
                registration=registration,
                initial_resources=init_resources,
            ))
        yield
    finally:
        for civ_registration in civ_registrations:
            # pylint: disable=protected-access
            flow_service._players_repo.register_player(civ_registration)
