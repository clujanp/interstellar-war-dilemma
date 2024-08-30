from random import choice
from typing import List, Dict
from app.core.interfaces.repositories.strategies import StrategyRepository
from app.infraestructure.logging import logger


class LocalStrategyRepository(StrategyRepository):
    STRATEGY_PATH: str  # path where strategies are stored
    SEARCH_PAHTERN: str  # search pattern for strategies in path
    BUILT_IN_STRATEGIES: Dict[str, callable]  # built-in strategies map

    def __init__(
        self,
        strategy_path: str,
        search_pattern: str,
        built_in_strategies: Dict[str, callable]
    ):
        self.STRATEGY_PATH = strategy_path
        self.SEARCH_PAHTERN = search_pattern
        self.BUILT_IN_STRATEGIES = built_in_strategies

    def load_strategies(self) -> dict[str, callable]:
        from importlib import import_module
        from inspect import getmembers, isfunction, ismethod, getmodule

        strategy_modules = self._map_strategy_modules()
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

    def _map_strategy_modules(self) -> List[str]:
        from glob import glob
        return [
            file.replace(
                f"{self.STRATEGY_PATH}", self.STRATEGY_PATH
            ).replace('/', '.')[:-3]
            for file in glob(f"{self.STRATEGY_PATH}/{self.SEARCH_PAHTERN}")
        ]

    def select_random_builtin(self) -> callable:
        return choice(list(self.BUILT_IN_STRATEGIES.values()))
