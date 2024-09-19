import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, call
from collections import OrderedDict
from app.utils.decorators import caster, cached


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


class TestUtilsDecoratorsCached(TestCase):
    def setUp(self):
        self.mock_function = MagicMock(side_effect=lambda x: x)
        self.cached_function = cached(self.mock_function)

    def test_cached_success(self):
        self.cached_function("input_value")
        self.mock_function.assert_called_once_with("input_value")
        assert (
            getattr(self.cached_function, 'cache_clear', None)
            and callable(self.cached_function.cache_clear)
        )

    def test_cached_with_same_input_success(self):
        self.cached_function("input_value")
        self.cached_function("input_value")
        self.mock_function.assert_called_once_with("input_value")

    def test_cached_with_similar_input_success(self):
        self.cached_function(1)
        self.cached_function(True)
        assert [call(1), call(True)] == self.mock_function.call_args_list
        assert self.mock_function.call_count == 2

    def test_cached_with_different_input_success(self):
        self.cached_function("input_value")
        self.cached_function("different_input")
        assert [
            call("input_value"), call("different_input")
        ] == self.mock_function.call_args_list
        assert self.mock_function.call_count == 2

    def test_cached_with_same_input_and_different_type_success(self):
        self.cached_function("input_value")
        self.cached_function(123)
        assert [
            call("input_value"), call(123)
        ] == self.mock_function.call_args_list
        assert self.mock_function.call_count == 2

    def test_cached_with_same_input_and_some_change_into_input_success(self):
        # mock object with attr=1 using as argument for cached function
        mock = MagicMock(attr=1)
        # call cached function with mock object and get its attr value
        response_1_attr = self.cached_function(mock).attr
        # change mock object attr value to 2
        mock.attr = 2
        # call cached function with mock object and get its attr value
        response_2_attr = self.cached_function(mock).attr
        # assert that cached function was called twice and with the same mock
        assert response_1_attr == 1 and response_2_attr == 2
        self.mock_function.assert_called_once_with(mock)
