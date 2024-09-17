from typing import List, Optional
from app.application.screens import Screen


class GameplayController:
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
