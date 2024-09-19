import init  # noqa: F401
from unittest import TestCase
from unittest.mock import patch
from app.utils.functions import (
    replace_decimals, replace_to_decimal, cast_datetime_to_isoformat,
    planet_namer, snake_to_pascal, to_snake
)
from decimal import Decimal
from datetime import datetime


class TestFunctions(TestCase):
    def test_replace_decimals_with_list_of_decimals_success(self):
        input_list = [Decimal('10.0'), Decimal('20.5'), Decimal('30')]
        expected_list = [10, 20.5, 30]

        result = replace_decimals(input_list)
        assert result == expected_list

    def test_replace_decimals_with_dict_of_decimals_success(self):
        input_dict = {
            'a': Decimal('10.0'), 'b': Decimal('20.5'), 'c': Decimal('30')}
        expected_dict = {'a': 10, 'b': 20.5, 'c': 30}

        result = replace_decimals(input_dict)
        assert result == expected_dict

    def test_replace_to_decimal_with_list_of_floats_success(self):
        input_list = [10.0, 20.5, 30.0]
        expected_list = [Decimal('10.0'), Decimal('20.5'), Decimal('30.0')]

        result = replace_to_decimal(input_list)
        assert result == expected_list

    def test_replace_to_decimal_with_dict_of_floats_success(self):
        input_dict = {'a': 10.0, 'b': 20.5, 'c': 30.0}
        expected_dict = {
            'a': Decimal('10.0'), 'b': Decimal('20.5'), 'c': Decimal('30.0')}

        result = replace_to_decimal(input_dict)
        assert result == expected_dict

    def test_cast_datetime_to_isoformat_with_list_of_datetimes_success(self):
        now = datetime.now()
        input_list = [now]
        expected_list = [now.isoformat()]

        result = cast_datetime_to_isoformat(input_list)
        assert result == expected_list

    def test_cast_datetime_to_isoformat_with_dict_of_datetimes_success(self):
        now = datetime.now()
        input_dict = {'now': now}
        expected_dict = {'now': now.isoformat()}

        result = cast_datetime_to_isoformat(input_dict)
        assert result == expected_dict

    @patch('app.utils.functions.choice')
    def test_planet_namer(self, mock_choice):
        mock_choice.side_effect = ['Zar', 'xis', ' II']
        result = planet_namer()
        assert result == 'Zarxis II'

    @patch('app.utils.functions.choice')
    def test_planet_namer_different_values(self, mock_choice):
        mock_choice.side_effect = ['Xil', 'on', ' Prime']
        result = planet_namer()
        assert result == 'Xilon Prime'

    def test_snake_to_pascal(self):
        assert snake_to_pascal('hello_world') == 'Hello World'

    def test_to_snake(self):
        assert to_snake('HelloWorld') == 'hello_world'
        assert to_snake('HELLO WORLD') == 'hello_world'
        assert to_snake('HELLO-WORLD') == 'hello_world'
        assert to_snake('hello-world') == 'hello_world'
        assert to_snake('HelloWorld') == 'hello_world'
        assert to_snake('Hello world') == 'hello_world'
        assert to_snake('Hello__world') == 'hello__world'
