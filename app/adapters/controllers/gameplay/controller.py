from typing import List, Optional
from app.infraestructure.screens import Screen
from app.infraestructure.logging import logger


class GameplayController:
    STRATEGY_PATH = 'gameplay/strategies'
    SEARCH_PAHTERN = f"{STRATEGY_PATH}/*.py"

    def __init__(self, starts='welcome', context: dict = None):
        self.finished = False
        self.next = starts
        self.args = []
        self._scenarios = {}
        self.screen = Screen()
        self.context = context or {}
        self.context['controller'] = self

    def run(self):
        while True:
            scenario = self.get_scenario()
            self.execute_process(scenario)
            if self.finished:
                break
            self.next, self.args = self.screen.prompt(
                scenario.prompt or self.screen.DEFAULT_PROMPT)
            logger.warn(f"{self.next = } {self.args = }")

    def get_scenario(self) -> callable:
        scenario = self._scenarios.get(self.next, None)
        assert scenario is not None, f'Invalid scenario: {self.next}'
        return scenario

    @staticmethod
    def scenario(
        command: str,
        template: str,
        prompt: Optional[str] = None,
        alias: List[str] = []
    ) -> callable:
        def decorator(scenario: callable) -> callable:
            scenario.template = template
            scenario.prompt = prompt
            scenario.command = command
            scenario.alias = alias
            return scenario
        return decorator

    def register_scenarios(self, *scenarios: List[callable]) -> None:
        for scenario in scenarios:
            self._scenarios[scenario.command] = scenario
            if scenario.alias:
                assert isinstance(scenario.alias, list)
                assert all(isinstance(alias, str) for alias in scenario.alias)
                assert all(
                    alias not in self._scenarios for alias in scenario.alias)
                for alias in scenario.alias:
                    self._scenarios[alias] = scenario

    def execute_process(self, scenario: callable) -> None:
        scenario(self.context, *self.args)
        self.screen.show(scenario.template, self.context)
        self.finished = self.context.get('finished', False)

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

    @classmethod
    def _map_strategy_modules(cls) -> List[str]:
        from glob import glob
        return [
            file.replace(
                f"{cls.STRATEGY_PATH}", cls.STRATEGY_PATH
            ).replace('/', '.')[:-3]
            for file in glob(cls.SEARCH_PAHTERN)
        ]
