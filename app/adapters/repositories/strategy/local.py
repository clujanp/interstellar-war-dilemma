from random import choice
from typing import List
from app.core.interfaces.repositories.strategies import StrategyRepository
from app.infraestructure.logging import logger
from gameplay.strategy import BuiltInStrategies


class LocalStrategyRepository(StrategyRepository):
    STRATEGY_PATH = 'gameplay/strategies'
    SEARCH_PAHTERN = f"{STRATEGY_PATH}/*.py"
    AVAILABLE_STRATEGIES = {
        'always_cooperation': BuiltInStrategies.always_cooperation,
        'always_aggression': BuiltInStrategies.always_aggression,
        'random': BuiltInStrategies.random,
        'reply_last': BuiltInStrategies.reply_last,
    }

    @classmethod
    def load_strategies(cls) -> dict[str, callable]:
        from importlib import import_module
        from inspect import getmembers, isfunction, ismethod, getmodule

        strategy_modules = cls._map_strategy_modules()
        functions = {}
        for mod_path in strategy_modules:
            module = import_module(mod_path)
            # get all functions of module
            found_functions = {
                **dict(getmembers(module, isfunction)),
                # support modular decorated strategies
                **dict(getmembers(module, ismethod))
            }

            # storage functions
            functions.update({
                name: func for name, func in found_functions.items()
                # when function from the same package of module
                if getmodule(func).__package__ == module.__package__
            })
        logger.debug(f"Loaded strategies: {functions}")
        return functions

    @classmethod
    def _map_strategy_modules(cls) -> List[str]:
        from glob import glob
        return [
            file.replace(
                f"{cls.STRATEGY_PATH}", cls.STRATEGY_PATH
            ).replace('/', '.')[:-3]
            for file in glob(cls.SEARCH_PAHTERN)
        ]

    @classmethod
    def select_random_builtin(cls) -> callable:
        return choice(list(cls.AVAILABLE_STRATEGIES.values()))
