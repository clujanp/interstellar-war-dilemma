from random import choice
from typing import List, Dict, Callable, Tuple
from app.core.interfaces.repositories.strategies import StrategyRepository
from app.infraestructure.logging import logger
from app.config.messages import ERR_LOCAL_REPOSITORY_STRATEGY as ERR_MSG


class LocalStrategyRepository(StrategyRepository):
    STRATEGY_PATH: str  # path where strategies are stored
    SEARCH_PAHTERN: str  # search pattern for strategies in path
    BUILT_IN_STRATEGIES: Dict[str, Callable]  # built-in strategies map

    def __init__(
        self,
        strategy_path: str,
        search_pattern: str,
        built_in_strategies: Dict[str, Callable]
    ):
        self.STRATEGY_PATH = strategy_path
        self.SEARCH_PAHTERN = search_pattern
        self.BUILT_IN_STRATEGIES = built_in_strategies

    def load_strategies(self) -> dict[str, Callable]:
        from importlib import import_module
        from inspect import getmembers, isfunction, ismethod, getmodule

        strategy_modules = self._map_strategy_modules()
        functions = {}
        for mod_path in strategy_modules:
            module = import_module(mod_path)
            # get all functions of module
            found_functions: List[Tuple[str, Callable]] = [
                *getmembers(module, isfunction),
                # support modular decorated strategies
                *getmembers(module, ismethod)
            ]
            # storage functions
            mod_functions: List[Tuple[str, Callable]] = [
                (name, func,) for name, func in found_functions
                # when function from the same package of module
                if getmodule(func).__package__ == module.__package__
            ]
            # check if there is more than one function in module
            if len(mod_functions) > 1:
                logger.warning(
                    ERR_MSG['warning_more_than_one'].format(mod_path))
                mod_functions = [mod_functions[0]]
            functions.update(mod_functions)

        logger.debug(ERR_MSG['debug_loaded'].format(functions))
        return functions

    def _map_strategy_modules(self) -> List[str]:
        from glob import glob
        return [
            file.replace(
                f"{self.STRATEGY_PATH}", self.STRATEGY_PATH
            ).replace('/', '.')[:-3]
            for file in glob(f"{self.STRATEGY_PATH}/{self.SEARCH_PAHTERN}")
        ]

    def select_random_builtin(self) -> Callable:
        return choice(list(self.BUILT_IN_STRATEGIES.values()))
