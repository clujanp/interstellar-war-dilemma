import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock
from app.infraestructure.screens.filters import (
    colorize_text, bold_text, tabulate, ljust, rjust, center, uppercase,
    lowercase, _round
)


class FiltersTestCase(TestCase):
    def setUp(self):
        self.text = "hello"
        self.color = "red"
        self.data = [MagicMock(attr1="value1", attr2="value2")]
        self.headers = ["attr1", "attr2"]

    def test_colorize_text_success(self):
        result = colorize_text(self.text, self.color)
        expected_result = f"\033[31m{self.text}\033[0m"
        assert result == expected_result

    def test_bold_text_success(self):
        result = bold_text(self.text)
        expected_result = f"\033[1m{self.text}\033[0m"
        assert result == expected_result

    def test_tabulate_success(self):
        result = tabulate(self.data, *self.headers)
        expected_result = (
            "Attr1  | Attr2 \n"
            "------ | ------\n"
            "value1 | value2\n"
        )
        assert result == expected_result

    def test_ljust_success(self):
        result = ljust(self.text, 10, '-')
        expected_result = "hello-----"
        assert result == expected_result

    def test_rjust_success(self):
        result = rjust(self.text, 10, '-')
        expected_result = "-----hello"
        assert result == expected_result

    def test_center_success(self):
        result = center(self.text, 10, '-')
        expected_result = "--hello---"
        assert result == expected_result

    def test_uppercase_success(self):
        result = uppercase(self.text)
        expected_result = "HELLO"
        assert result == expected_result

    def test_lowercase_success(self):
        result = lowercase(self.text)
        expected_result = "hello"
        assert result == expected_result

    def test_round_success(self):
        result = _round(3.14159, 2)
        expected_result = 3.14
        assert result == expected_result  # NOSONAR: S1244

    def test_round_no_ndigits_success(self):
        result = _round(3.14159)
        expected_result = 3
        assert result == expected_result
