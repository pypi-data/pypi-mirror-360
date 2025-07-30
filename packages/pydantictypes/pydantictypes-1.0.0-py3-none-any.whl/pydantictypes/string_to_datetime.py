"""Custom data type to convert string to datetime."""

from abc import abstractmethod
from datetime import datetime
from typing import Any

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core.core_schema import no_info_after_validator_function

__all__ = [
    "StringSlashMonthDayOnlyToDatetime",
    "StringSlashToDateTime",
]


class StringToDateTime(datetime):
    """Type that converts string to datetime."""

    @classmethod
    # Reason: To follow Pydantic specification pylint: disable-next=line-too-long
    def __get_pydantic_core_schema__(cls, _source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:  # noqa: ANN401
        return no_info_after_validator_function(cls.validate, handler.generate_schema(str))

    @classmethod
    # Reason: This Any is correct
    def validate(cls, value: Any) -> datetime:  # noqa: ANN401
        value = cls.datetime_must_be_from_str(value)
        return cls.parse_date(value)

    @classmethod
    # Reason: This Any is correct
    def datetime_must_be_from_str(cls, value: Any) -> str:  # noqa: ANN401
        if not isinstance(value, str):
            msg = "string required"
            raise TypeError(msg)
        return value

    @classmethod
    # Reason: This Any is correct
    def parse_date(cls, value: Any) -> datetime:  # noqa: ANN401
        # Reason: Time is not used in this process.
        return datetime.strptime(value, cls.get_format())  # noqa: DTZ007

    @classmethod
    @abstractmethod
    def get_format(cls) -> str:
        raise NotImplementedError


class StringSlashToDateTime(StringToDateTime):
    """Type that converts string to datetime."""

    @classmethod
    def get_format(cls) -> str:
        return "%Y/%m/%d"


class StringNumberOnlyToDateTime(StringToDateTime):
    """Type that converts string to datetime."""

    @classmethod
    # Reason: This Any is correct
    def validate(cls, value: Any) -> datetime:  # noqa: ANN401
        value = cls.datetime_must_be_from_str(value)
        value = cls.eight_digits_required(value)
        return cls.parse_date(value)

    @classmethod
    def eight_digits_required(cls, value: str) -> str:
        number_digit = 8
        if len(value) != number_digit:
            msg = "8 digits required"
            raise ValueError(msg)
        return value

    @classmethod
    def get_format(cls) -> str:
        return "%Y%m%d"


class StringSlashMonthDayOnlyToDatetime(StringToDateTime):
    """Type that converts string to datetime."""

    @classmethod
    # Reason: This Any is correct
    def parse_date(cls, value: Any) -> datetime:  # noqa: ANN401
        if not isinstance(value, str):
            msg = "string required"
            raise TypeError(msg)
        # Reason: Time is not used in this process.
        return datetime.strptime(f"1904/{value}", cls.get_format())  # noqa: DTZ007

    @classmethod
    def get_format(cls) -> str:
        return "%Y/%m/%d"
