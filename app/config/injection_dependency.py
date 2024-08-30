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
    from app.adapters.repositories.strategy.proxies import SecureProxyFactory
    from app.config.secure_proxies import SECURITY_PROXY
    from app.config.local_strategies_repository import REPO_CONFIG

    planet_service = PlanetService()
    civilization_service = CivilizationService()

    strategy_repo = StrategyRepository(**REPO_CONFIG)
    strategy_proxy_factory = SecureProxyFactory(SECURITY_PROXY)
    strategy_service = StrategyService(strategy_repo, strategy_proxy_factory)

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
