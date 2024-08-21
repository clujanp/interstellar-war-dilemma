from jinja2 import Environment, FileSystemLoader
from typing import List, Tuple, Optional
from .filters import (
    colorize_text, tabulate, bold_text,
    ljust, rjust, center, uppercase, lowercase, _round
)


class Screen:
    TEMPLATES_ROOT = 'app/infraestructure/screens/templates'
    DEFAULT_PROMPT = '> '

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(self.TEMPLATES_ROOT))
        self.env.filters['colorize'] = colorize_text
        self.env.filters['tabulate'] = tabulate
        self.env.filters['bold'] = bold_text
        self.env.filters['ljust'] = ljust
        self.env.filters['rjust'] = rjust
        self.env.filters['center'] = center
        self.env.filters['upper'] = uppercase
        self.env.filters['lower'] = lowercase
        self.env.filters['round'] = _round

    def show(self, template: str, context: dict) -> None:
        template = self.env.get_template(template)
        output = template.render(context)
        print(output)

    @classmethod
    def prompt(cls, message: str) -> Tuple[Optional[str], List[str]]:
        input_ = input(message or cls.DEFAULT_PROMPT)
        input_ = [part.lower() for part in input_.split()]
        if not input_:
            return None, []
        return input_[0], input_[1:]
