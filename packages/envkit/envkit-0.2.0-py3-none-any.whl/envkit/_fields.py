from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING, Protocol, TypedDict, final, overload

if TYPE_CHECKING:
    from enum import Enum
    from types import EllipsisType
    from typing import Unpack

type Unset = EllipsisType


class ParserFactory[T, **P](Protocol):
    def __call__(
        self, name: str, raw_value: str, *args: P.args, **kwargs: P.kwargs
    ) -> T: ...


@final
class EnvField[T, **P]:
    __slots__ = ("factory",)

    def __init__(self, factory: ParserFactory[T, P]) -> None:
        self.factory = factory

    @overload
    def __call__(
        self,
        name: str,
        default: T | Unset = ...,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T: ...

    @overload
    def __call__(
        self, name: str, default: None, *args: P.args, **kwargs: P.kwargs
    ) -> T | None: ...

    def __call__(
        self,
        name: str,
        default: T | None | Unset = ...,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T | None:
        """Parse an environment variable.

        Args:
            name: Environment variable name
            default: Default value if variable is not set. Let unset
                    to require the variable. Use None to allow None return.
            *args: Additional arguments passed to the factory
            **kwargs: Validation constraints passed to the factory

        Returns:
            The parsed and validated value, or the default if variable is unset

        Raises:
            ValueError: If the variable is required but not set, or if parsing/validation fails
        """
        raw_value = getenv(name)
        if raw_value is None:
            if default is ...:
                raise ValueError(f"Environment variable '{name}' is not set.")
            return default

        return self.factory(name, raw_value, *args, **kwargs)


class StrConstraints(TypedDict, total=False):
    min_length: int
    max_length: int


def parse_str(name: str, raw_value: str, **constraints: Unpack[StrConstraints]) -> str:
    min_length = constraints.get("min_length")
    if min_length is not None and len(raw_value) < min_length:
        raise ValueError(
            f"Environment variable '{name}' is shorter than the minimum length {min_length}."
        )
    max_length = constraints.get("max_length")
    if max_length is not None and len(raw_value) > max_length:
        raise ValueError(
            f"Environment variable '{name}' is longer than the maximum length {max_length}."
        )
    return raw_value


class IntConstraints(TypedDict, total=False):
    min_value: int
    max_value: int


def parse_int(name: str, raw_value: str, **constraints: Unpack[IntConstraints]) -> int:
    min_val = constraints.get("min_value")
    max_val = constraints.get("max_value")
    if min_val is not None and max_val is not None and min_val > max_val:
        raise ValueError("min_value cannot be greater than max_value")

    try:
        value = int(raw_value.strip())
    except ValueError as error:
        raise ValueError(
            f"Environment variable '{name}' must be an integer, got '{raw_value}'."
        ) from error

    if min_val is not None and value < min_val:
        raise ValueError(
            f"Environment variable '{name}' is less than the minimum value {min_val}."
        )
    if max_val is not None and value > max_val:
        raise ValueError(
            f"Environment variable '{name}' is greater than the maximum value {max_val}."
        )
    return value


def parse_bool(name: str, raw_value: str) -> bool:
    match raw_value.strip().lower():
        case "true" | "1" | "yes" | "on":
            return True
        case "false" | "0" | "no" | "off":
            return False
        case _:
            raise ValueError(
                f"Environment variable '{name}' must be a boolean, got '{raw_value}'."
            )


def parse_enum[T: Enum](name: str, raw_value: str, *, enum: type[T]) -> T:
    for member in enum:
        if member.name.lower() == raw_value.strip().lower():
            return member

    valid_values = [e.name.lower() for e in enum]
    raise ValueError(
        f"Environment variable '{name}' must be one of {valid_values}, got '{raw_value}'."
    )


@final
class Fields:
    """Public interface for parsing environment variables with type safety.

    This class provides pre-configured field parsers for common data types.
    Each field type supports validation constraints and proper error handling.

    Attributes:
        str: Parser for string values with length validation
        int: Parser for integer values with range validation
        bool: Parser for boolean values (supports multiple formats)
        enum: Parser for enum values by member name

    Example:
        ```python
        # Required string with minimum length
        api_key = Fields.str("API_KEY", min_length=32)

        # Optional integer with default and range
        port = Fields.int("PORT", default=8080, min_value=1, max_value=65535)

        # Boolean with default
        debug = Fields.bool("DEBUG", default=False)

        # Enum parsing
        log_level = Fields.enum("LOG_LEVEL", enum=LogLevel, default=LogLevel.INFO)
        ```
    """

    str = EnvField(parse_str)
    """String field parser with optional length validation."""

    int = EnvField(parse_int)
    """Integer field parser with optional range validation."""

    bool = EnvField(parse_bool)
    """Boolean field parser supporting multiple boolean formats.

    Accepts: true/false, 1/0, yes/no, on/off
    """

    enum = EnvField(parse_enum)
    """Enum field parser that matches by member name (case-insensitive)."""
