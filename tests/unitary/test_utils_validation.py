import init  # noqa: F401
from unittest import TestCase
from unittest.mock import MagicMock, patch
from utils.validation import (
    validate_not_empty_or_whitespaces,
    validate_max_length,
    validate_min_length,
    validate_unique,
    validate_in_options,
    validate_is_instance,
    validate_email,
    validate_not_future,
    validate_length,
)
from datetime import datetime


class TestsUtilsValidation(TestCase):
    def setUp(self):
        self.mocked_datetime_now = MagicMock(
            return_value=datetime(2023, 1, 1, 12, 0, 0))
        self.msg = "assert message"

    def test_validate_not_empty_or_whitespaces_success(self):
        validate_not_empty_or_whitespaces("valid input", self.msg)
        # No exception means success

    def test_validate_not_empty_or_whitespaces_fail(self):
        with self.assertRaises(AssertionError):
            validate_not_empty_or_whitespaces(" ", self.msg)

    def test_validate_max_length_success(self):
        validate_max_length("short", 10, self.msg)
        # No exception means success

    def test_validate_max_length_fail(self):
        with self.assertRaises(AssertionError):
            validate_max_length("too long value", 5, self.msg)

    def test_validate_min_length_success(self):
        validate_min_length("long enough", 5, self.msg)
        # No exception means success

    def test_validate_min_length_fail(self):
        with self.assertRaises(AssertionError):
            validate_min_length("short", 10, self.msg)

    def test_validate_unique_success(self):
        validate_unique([1, 2, 3], self.msg)
        # No exception means success

    def test_validate_unique_fail(self):
        with self.assertRaises(AssertionError):
            validate_unique([1, 1, 2], self.msg)

    def test_validate_in_options_success(self):
        validate_in_options("a", ["a", "b", "c"], self.msg)
        # No exception means success

    def test_validate_in_options_fail(self):
        with self.assertRaises(AssertionError):
            validate_in_options("d", ["a", "b", "c"], self.msg)

    def test_validate_is_instance_success(self):
        validate_is_instance("string", str, self.msg)
        # No exception means success

    def test_validate_is_instance_fail(self):
        with self.assertRaises(AssertionError):
            validate_is_instance(123, str, self.msg)

    def test_validate_email_success(self):
        validate_email("email@example.com", self.msg)
        # No exception means success

    def test_validate_email_fail(self):
        with self.assertRaises(AssertionError):
            validate_email("not-an-email", self.msg)

    def test_validate_not_future_success(self):
        with self.mocked_datetime_now:
            validate_not_future(datetime(2022, 12, 31, 11, 59, 59), self.msg)
            # No exception means success

    @patch('utils.validation.datetime')
    def test_validate_not_future_fail(self, mock_datetime: MagicMock):
        mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        with self.assertRaises(AssertionError):
            validate_not_future(datetime(2023, 1, 1, 12, 0, 1), self.msg)

    def test_validate_length_success(self):
        validate_length("valid length", 5, 15, "Length out of range")

    def test_validate_length_min_fail(self):
        with self.assertRaises(AssertionError) as context:
            validate_length("short", 10, 15, "Length out of range")
        assert "Length out of range" == str(context.exception)

    def test_validate_length_max_fail(self):
        with self.assertRaises(AssertionError) as context:
            validate_length("too long value", 5, 10, "Length out of range")
        assert "Length out of range" == str(context.exception)
