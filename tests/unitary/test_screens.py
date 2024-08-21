import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from app.infraestructure.screens import Screen


class TestScreen(TestCase):
    def setUp(self):
        self.mock_env = MagicMock()
        self.mock_template = MagicMock()
        self.mock_env.get_template.return_value = self.mock_template
        self.screen = Screen()
        self.screen.env = self.mock_env

    def test_show_success(self):
        template_name = 'test_template.html'
        context = {'key': 'value'}
        self.mock_template.render.return_value = 'Rendered Output'

        with patch('builtins.print') as mock_print:
            self.screen.show(template_name, context)
            self.mock_env.get_template.assert_called_once_with(template_name)
            self.mock_template.render.assert_called_once_with(context)
            mock_print.assert_called_once_with('Rendered Output')

    def test_prompt_success(self):
        message = 'Enter command: '
        with patch(
            'builtins.input', return_value='command arg1 arg2'
        ) as mock_input:
            command, args = self.screen.prompt(message)
            assert command == 'command'
            assert args == ['arg1', 'arg2']
            mock_input.assert_called_once_with(message)

    def test_prompt_empty_fail(self):
        message = 'Enter command: '
        with patch('builtins.input', return_value='') as mock_input:
            command, args = self.screen.prompt(message)
            assert command is None
            assert args == []
            mock_input.assert_called_once_with(message)
