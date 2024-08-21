from app.utils.typing import List, Email, Iterable
from datetime import datetime


def validate_not_empty_or_whitespaces(value: str, message: str) -> None:
    assert value.strip(), message


def validate_max_length(value: Iterable, max_len: int, message: str) -> None:
    assert len(value) <= max_len, message


def validate_min_length(value: Iterable, min_len: int, message: str) -> None:
    assert len(value) >= min_len, message


def validate_length(
    value: Iterable, min_len: int, max_len: int, message: str
) -> None:
    assert min_len <= len(value) <= max_len, message


def validate_unique(value: List[any], message: str) -> None:
    assert len(value) == len(set(value)), message


def validate_in_options(value: str, options: List[str], message: str) -> None:
    assert value in options, message


def validate_is_instance(value: any, type: any, message: str) -> None:
    assert isinstance(value, type), message


def validate_email(value: Email, message: str) -> None:
    from re import match
    assert match(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$', value), message


def validate_not_future(value: datetime, message: str) -> None:
    assert value <= datetime.now(), message
