from app.adapters.controllers.gameplay.controller import GameplayController


def get_gameplay_controller() -> GameplayController:
    from app.adapters.controllers.gameplay.controller import GameplayController
    from app.adapters.controllers.gameplay.scenarios import (
        welcome, start, rounds, summary, end)
    from app.adapters.repositories.strategy import StrategyRepository
    from app.core.domain.services import (
        PlanetService, StrategyService, CivilizationService, RoundService,
        SkirmishService
    )
    from app.core.interfaces.use_cases import (
        PlanetUseCases, StrategiesUseCases, CivilizationUseCases,
        SkirmishUseCases, RoundUseCases, MemoriesUseCases
    )

    planet_service = PlanetService()
    civilization_service = CivilizationService()
    strategy_service = StrategyService(StrategyRepository())

    gameplay = GameplayController(
        starts='welcome',
        context={
            'title': "Civilization War",
            'use_cases': {
                'planet': PlanetUseCases(planet_service),
                'strategies': StrategiesUseCases(
                    strategy_service, planet_service, civilization_service),
                'civilizations': CivilizationUseCases(civilization_service),
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
