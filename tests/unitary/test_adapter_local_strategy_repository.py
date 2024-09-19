import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.adapters.repositories.strategy.local import LocalStrategyRepository


class TestLocalStrategyRepository(TestCase):
    def setUp(self):
        self.mock_strategy = MagicMock(__package__='path.to.strategy')
        self.mock_foreign_funct = MagicMock(__package__='other.path')
        self.mock_builtin_strategy = MagicMock()
        self.repository = LocalStrategyRepository(
            strategy_path='path/to/strategies',
            search_pattern='*.py',
            built_in_strategies={'test_strategy': self.mock_builtin_strategy},
        )

    def test_instace_repository_success(self):
        assert self.repository.STRATEGY_PATH == 'path/to/strategies'
        assert self.repository.SEARCH_PAHTERN == '*.py'
        assert self.repository.BUILT_IN_STRATEGIES == {
            'test_strategy': self.mock_builtin_strategy}

    @patch('importlib.import_module')
    @patch('logging.Logger.warning')
    @patch('inspect.getmodule')
    @patch('inspect.getmembers')
    def test_load_strategies_success(
        self,
        mock_getmembers: MagicMock,
        mock_getmodule: MagicMock,
        mock_logger_warn: MagicMock,
        mock_import_module: MagicMock,
    ):
        from inspect import isfunction, ismethod

        self.repository._map_strategy_modules = MagicMock(
            return_value=['path.to.strategy'])
        mock_import_module.return_value = MagicMock(
            __package__='path.to.strategy')
        mock_getmembers.side_effect = [[
            ('mock_func', self.mock_strategy,),
            ('mock_func_2', self.mock_strategy,),
            ('mock_foreign_func', self.mock_foreign_funct,),
        ], []]
        mock_getmodule.side_effect = [
            MagicMock(__package__='path.to.strategy'),
            MagicMock(__package__='path.to.strategy'),
            MagicMock(__package__='other.path'),
        ]
        functions = self.repository.load_strategies()
        assert functions == {'mock_func': self.mock_strategy}
        self.repository._map_strategy_modules.assert_called_once_with()
        mock_import_module.assert_called_once_with('path.to.strategy')
        assert [
            call(mock_import_module.return_value, isfunction),
            call(mock_import_module.return_value, ismethod),
        ] == mock_getmembers.call_args_list
        assert [
            call(self.mock_strategy),
            call(self.mock_strategy),
            call(self.mock_foreign_funct),
        ] == mock_getmodule.call_args_list
        mock_logger_warn.assert_called_once_with(
            'More than one strategy found in path.to.strategy')

    @patch('glob.glob')
    def test_map_strategy_modules_success(self, mock_glob: MagicMock):
        mock_glob.return_value = [
            'path/to/strategies/strategy1.py',
            'path/to/strategies/strategy2.py',
        ]
        modules = self.repository._map_strategy_modules()
        assert modules == [
            'path.to.strategies.strategy1', 'path.to.strategies.strategy2']
        mock_glob.assert_called_once_with('path/to/strategies/*.py')

    @patch('app.adapters.repositories.strategy.local.choice')
    def test_select_random_builtin_success(self, mock_choice: MagicMock):
        mock_choice.return_value = self.mock_builtin_strategy
        strategy = self.repository.select_random_builtin()
        assert strategy == self.mock_builtin_strategy
        mock_choice.assert_called_once_with(
            list(self.repository.BUILT_IN_STRATEGIES.values()))
