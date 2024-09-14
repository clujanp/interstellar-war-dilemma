import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock
from collections import OrderedDict
from app.utils.decorators import caster


class TestUtilsDecoratorsCaster(TestCase):
    def setUp(self):
        self.casted_input = "expected_casted_return_value"
        self.mock_function = MagicMock(return_value=self.casted_input)
        self.cast_func = caster(type=str)(self.mock_function)

    def test_caster_use_success(self):
        caster(type=int)(self.mock_function)

    def test_caster_use_with_invalid_type_fail(self):
        with self.assertRaises(AssertionError):
            caster(type=list)(self.mock_function)
        with self.assertRaises(AssertionError):
            caster(type=tuple)(self.mock_function)
        with self.assertRaises(AssertionError):
            caster(type=dict)(self.mock_function)
        with self.assertRaises(AssertionError):
            caster(type=OrderedDict)(self.mock_function)

    def test_caster_success(self):
        result = self.cast_func("input_value")
        self.mock_function.assert_called_once_with("input_value")
        assert result == self.casted_input

    def test_caster_without_cast_success(self):
        result = self.cast_func(123)
        self.mock_function.assert_not_called()
        assert result == 123

    def test_caster_with_invalid_obj_fail(self):
        self.mock_function.configure_mock(
            side_effect=ValueError("Invalid input"))
        with self.assertRaises(ValueError):
            self.cast_func("invalid_input")

    def test_caster_with_complex_input_sucess(self):
        input_ = {'k1': 1, 'k2': {0, 0.1}, 'k3': [1, 2, 3], 'k4': 'string'}
        result = self.cast_func(input_)
        self.mock_function.assert_called_once_with('string')
        assert result == {**input_, 'k4': self.casted_input}
