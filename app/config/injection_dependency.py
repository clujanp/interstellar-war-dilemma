from app.adapters.controllers.gameplay.controller import GameplayController


def get_gameplay_controller() -> GameplayController:
    from app.adapters.controllers.gameplay.controller import GameplayController
    from app.adapters.controllers.gameplay.scenarios import (
        welcome, start, rounds, summary, end)
    from app.core.domain.services import (
        PlanetService, CivilizationService, RoundService, SkirmishService)
    from app.core.interfaces.use_cases import (
        PlanetUseCases, CivilizationUseCases, SkirmishUseCases, RoundUseCases,
        MemoriesUseCases
    )

    gameplay = GameplayController(
        starts='welcome',
        context={
            'title': "Civilization War",
            'use_cases': {
                'planet': PlanetUseCases(PlanetService()),
                'civilizations': CivilizationUseCases(CivilizationService()),
                'skirmish': SkirmishUseCases(SkirmishService()),
                'round': RoundUseCases(RoundService()),
                'memories': MemoriesUseCases(),
            },
            'config': {
                'initial_resources': 100,
                'complementary_civilization_name': 'Barbarians',
            }
        }
    )
    gameplay.context['memories'] = gameplay.context['use_cases']['memories']
    gameplay.register_scenarios(welcome, start, rounds, summary, end)
    return gameplay
