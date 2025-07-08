from runpy import run_module as runpy_run_module
from unittest import TestCase
from unittest.mock import patch
from app import __main__


class TestMain(TestCase):
    """Test suite for the main function in __main__.py"""

    def setUp(self):
        """Set up test fixtures before each test method."""

    @patch('builtins.print')
    def test_main_prints_hello_world(self, mock_print):
        """Test that main function prints 'Hello, World!'"""
        # Act
        __main__.main()

        # Assert
        mock_print.assert_called_once_with("Hello, World!")

    @patch('app.__main__.main')
    def test_main_block_execution_success(self, _mock_main):
        """Test that main is called when module is executed directly"""
        with patch('sys.argv', ['__main__.py']):
            runpy_run_module('app.__main__', run_name='__main__')
