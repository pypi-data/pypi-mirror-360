"""Custom data types."""

from __future__ import annotations

from contextlib import suppress
from decimal import Decimal
from sys import version_info
from typing import Optional
from typing import Union

from pydantic import BeforeValidator

from pydantictypes.abstract_string_to_optional_int import OptionalIntegerMustBeFromStr
from pydantictypes.abstract_string_to_optional_int import abstract_constringtooptionalint
from pydantictypes.validators import optional_int_validator
from pydantictypes.validators import optional_number_multiple_validator
from pydantictypes.validators import optional_number_size_validator

# Reason: To use raw typing imports pylint: disable=duplicate-code
try:
    from typing import Annotated
except ImportError:
    # Reason: Maybe mypy's bug
    from typing_extensions import Annotated  # type: ignore[assignment]
with suppress(ImportError):
    from typing import Unpack

__all__ = [
    "ConstrainedStringToOptionalInt",
]

Number = Union[int, float, Decimal]


# Reason: Followed Pydantic specification.
def constringtooptionalint(  # noqa: PLR0913 pylint: disable=too-many-arguments
    *,
    strict: bool | None = None,
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
    multiple_of: int | None = None,
) -> type[int | None]:
    """A wrapper around `int` that allows for additional constraints.

    Args:
        strict: Whether to validate the integer in strict mode. Defaults to `None`.
        gt: The value must be greater than this.
        ge: The value must be greater than or equal to this.
        lt: The value must be less than this.
        le: The value must be less than or equal to this.
        multiple_of: The value must be a multiple of this.

    Returns:
        The wrapped integer type.
    """
    constraints = abstract_constringtooptionalint(strict=strict, gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of)
    before_validator = BeforeValidator(OptionalIntegerMustBeFromStr(int).validate)
    # Reason: Following block is tested in different workflows in GitHub Actions
    if version_info < (3, 11):  # pragma: no cover
        # Filter out None values
        valid_constraints = tuple(c for c in constraints if c is not None)
        # Reason: Cannot use star expression in index on Python 3.7 (syntax was added in Python 3.11)
        annotations = (Optional[int], before_validator) + valid_constraints  # noqa: RUF005
        return Annotated[annotations]  # type: ignore[return-value]
    return Annotated[Optional[int], before_validator, Unpack[constraints]]  # type: ignore[return-value]


ConstrainedStringToOptionalInt = Annotated[
    Optional[int],
    BeforeValidator(OptionalIntegerMustBeFromStr(int).validate),
    optional_int_validator,
    optional_number_size_validator,
    optional_number_multiple_validator,
]
